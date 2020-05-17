from __future__ import annotations
import typing as t
import typing_extensions as tx

import logging
import dataclasses
from collections import defaultdict
from miniconfig import Configurator as _Configurator
from miniconfig import Context as _Context
from miniconfig.exceptions import ConfigurationError
from . import types
from .langhelpers import reify, fullname

if t.TYPE_CHECKING:
    import pathlib

logger = logging.getLogger(__name__)


class SettingsDict(tx.TypedDict, total=False):
    rootdir: str
    here: str


@dataclasses.dataclass
class Registry:
    settings: SettingsDict

    generators: t.Dict[str, t.List[t.Callable[..., t.Any]]] = dataclasses.field(
        default_factory=lambda: defaultdict(list), hash=False
    )
    _factories: t.Dict[str, t.List[types.ComponentFactory]] = dataclasses.field(
        default_factory=lambda: defaultdict(list), hash=False
    )
    _dryrun_factories: t.Dict[str, t.List[types.ComponentFactory]] = dataclasses.field(
        default_factory=lambda: defaultdict(list), hash=False
    )

    dry_run: t.Optional[bool] = None

    @reify
    def factories(self) -> t.Dict[str, t.List[types.ComponentFactory]]:
        if self.dry_run is None:
            raise RuntimeError("this registry is not configured")
        return self._dryrun_factories if self.dry_run else self._factories

    def configure(self, *, dry_run: bool = False) -> None:
        self.dry_run = dry_run


class Context(_Context):
    @reify
    def registry(self) -> Registry:
        return Registry(settings=t.cast(SettingsDict, self.settings))

    committed: t.ClassVar[bool] = False
    run: t.Optional[t.Callable[[t.Optional[t.List[str]]], t.Any]] = None


class App(_Configurator):
    context_factory = Context

    @property
    def registry(self) -> Registry:
        return self.context.registry  # type: ignore

    # default directives
    def register_factory(self, name: str, factory: types.ComponentFactory) -> None:
        type_ = types.ACTUAL_COMPONENT
        self.registry._factories[name].append(factory)
        self.action((name, type_), _noop)

    def register_dryurn_factory(
        self, name: str, factory: types.ComponentFactory
    ) -> None:
        type_ = types.DRYRUN_COMPONENT
        self.registry._dryrun_factories[name].append(factory)
        self.action((name, type_), _noop)

    def commit(self, *, dry_run: bool = False) -> None:
        from . import runtime

        # only once
        if self.context.committed:  # type: ignore
            return

        self.context.committed = True  # type: ignore

        logger.debug("commit")
        super().commit()
        self.registry.configure(dry_run=dry_run)
        runtime.set_context(runtime.RuntimeContext(self.registry, dry_run=dry_run))

    def describe(self) -> None:
        self.commit(dry_run=False)

        import json
        import inspect

        defs = {}
        for kit, fns in self.registry.generators.items():
            for fn in fns:
                name = f"{fn.__module__}.{fn.__name__}".replace("__main__.", "")
                summary = (inspect.getdoc(fn) or "").strip().split("\n", 1)[0]
                defs[name] = {"doc": summary, "generator": kit}

        factories = {
            name: [fullname(x) for x in xs]  # type: ignore
            for name, xs in self.registry.factories.items()
        }
        d = {"definitions": defs, "factories": factories}
        print(json.dumps(d, indent=2, ensure_ascii=False))

    def generate(
        self,
        *,
        targets: t.Optional[t.List[str]] = None,
        rootdir: t.Optional[str] = None,
    ) -> None:
        root_path = get_root_path(self.settings, root=rootdir)
        self.commit(dry_run=False)

        for kit, fns in self.registry.generators.items():
            walk_or_module = self.maybe_dotted(kit)
            if callable(walk_or_module):
                walk = walk_or_module
            elif hasattr(walk_or_module, "walk"):
                walk = walk_or_module.walk  # type: ignore
            else:
                # TODO: genetle error message
                raise ConfigurationError("{kit!r} is not callable")

            if not targets:
                sources = {fn.__name__: fn for fn in fns}
            else:
                sources = {fn.__name__: fn for fn in fns if fn.__name__ in targets}
            walk(sources, root=root_path)

    def scan(
        self,
        *,
        targets: t.Optional[t.List[str]] = None,
        rootdir: t.Optional[str] = None,
        out: t.Optional[str] = None,
        relative: bool = True,
    ) -> None:
        import contextlib
        import os
        from egoist.components.tracker import get_tracker

        self.include("egoist.components.tracker")
        self.commit(dry_run=True)

        if not bool(os.environ.get("VERBOSE", "")):
            logging.getLogger("prestring.output").setLevel(logging.WARNING)
        self.generate(targets=targets, rootdir=rootdir)

        root_path = get_root_path(self.settings, root=rootdir)
        deps = get_tracker().get_dependencies(root=root_path, relative=relative)

        with contextlib.ExitStack() as s:
            out_port: t.Optional[t.IO[str]] = None
            if out is not None:
                out_port = s.enter_context(open(out, "w"))

            print(deps, file=out_port)

    def run(self, argv: t.Optional[t.List[str]] = None) -> t.Any:
        import argparse
        from egoist.internal.logutil import logging_setup

        run_ = self.context.run  # type: ignore
        if run_ is not None:
            return run_(argv)

        # todo: scan modules in show_help only
        target_choices = [
            fn.__name__ for fns in self.registry.generators.values() for fn in fns
        ]

        parser = argparse.ArgumentParser(
            formatter_class=type(
                "_HelpFormatter",
                (argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter),
                {},
            )
        )
        parser.print_usage = parser.print_help  # type: ignore
        subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")
        subparsers.required = True

        # describe (todo: rename to info? or inspect?)
        fn = self.describe
        sub_parser = subparsers.add_parser(
            fn.__name__, help=fn.__doc__, formatter_class=parser.formatter_class
        )
        sub_parser.set_defaults(subcommand=fn)

        # generate
        fn = self.generate
        sub_parser = subparsers.add_parser(
            fn.__name__, help=fn.__doc__, formatter_class=parser.formatter_class
        )
        sub_parser.add_argument("--rootdir", required=False, help="-")
        sub_parser.add_argument("targets", nargs="*", choices=[[]] + target_choices)  # type: ignore
        sub_parser.set_defaults(subcommand=fn)

        # scan
        fn = self.scan
        sub_parser = subparsers.add_parser(
            fn.__name__, help=fn.__doc__, formatter_class=parser.formatter_class
        )
        sub_parser.add_argument("--rootdir", required=False, help="-")
        sub_parser.add_argument("targets", nargs="*", choices=[[]] + target_choices)  # type: ignore
        sub_parser.add_argument("--out")
        sub_parser.set_defaults(subcommand=fn)

        activate = logging_setup(parser)

        def _run(argv: t.Optional[t.List[str]] = None) -> t.Any:
            args = parser.parse_args(argv)
            params = vars(args).copy()
            activate(params)
            subcommand = params.pop("subcommand")
            return subcommand(**params)

        self.context.run = _run  # type:ignore
        return _run(argv)


def parse_args(
    argv: t.Optional[t.List[str]] = None, *, sep: str = "-"
) -> t.Iterator[t.List[str]]:
    """for bulk action"""
    import sys
    import itertools

    argv = argv or sys.argv[1:]
    itr = iter(argv)
    while True:
        argv = list(itertools.takewhile(lambda x: x != sep, itr))
        if len(argv) == 0:
            break
        yield argv
    assert not argv


def get_root_path(
    settings: SettingsDict, *, root: t.Optional[str] = None
) -> pathlib.Path:
    import pathlib

    if root is not None:
        return pathlib.Path(root)

    here = settings["here"]
    rootdir = settings["rootdir"]
    return pathlib.Path(here).parent / rootdir


def _noop() -> None:
    pass

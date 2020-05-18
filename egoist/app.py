from __future__ import annotations
import typing as t
import typing_extensions as tx

import logging
import dataclasses
from collections import defaultdict
from miniconfig import Configurator as _Configurator
from miniconfig import Context as _Context
from . import types
from .langhelpers import reify

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
    _task_list: t.List[t.Union[t.List[None], str]] = dataclasses.field(
        default_factory=lambda: [[]], hash=False
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

    def run(self, argv: t.Optional[t.List[str]] = None) -> t.Any:
        import argparse
        from egoist.internal.logutil import logging_setup

        run_ = self.context.run  # type: ignore
        if run_ is not None:
            return run_(argv)

        # todo: scan modules in show_help only
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

        # todo: remove this code
        # todo: anyFunction, more strict typing
        def _add_subcommand(
            app: App, setup: t.Callable[[App], None], *, fn: types.AnyFunction
        ) -> None:
            sub_parser = subparsers.add_parser(
                fn.__name__, help=fn.__doc__, formatter_class=parser.formatter_class
            )
            setup(app, sub_parser, fn)

        self.add_directive("add_subcommand", _add_subcommand)
        self.include("egoist.commands.describe")
        self.include("egoist.commands.generate")
        self.include("egoist.commands.scan")

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

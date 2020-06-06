from __future__ import annotations
import typing as t
import typing_extensions as tx

import logging
import dataclasses
from functools import partial
from collections import defaultdict
from miniconfig import Configurator as _Configurator
from miniconfig import Context as _Context
from . import types
from .langhelpers import reify

if t.TYPE_CHECKING:
    import pathlib
    from argparse import ArgumentParser

AnyFunction = t.Callable[..., t.Any]
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
    committed: t.ClassVar[bool] = False
    run: t.Optional[t.Callable[[t.Optional[t.List[str]]], t.Any]] = None

    @reify
    def registry(self) -> Registry:
        return Registry(settings=t.cast(SettingsDict, self.settings))

    @reify
    def _aggressive_import_cache(self) -> t.Set[t.Union[str, t.Callable[..., t.Any]]]:
        return set()  # for subapp

    @reify
    def _delayed_include_mapping(
        self,
    ) -> t.Dict[
        t.Callable[..., None],
        t.List[t.Tuple[App, t.Union[t.Callable[..., t.Any], str]]],
    ]:
        return defaultdict(list)

    @reify
    def cli_parser(self) -> ArgumentParser:
        import argparse

        # todo: scan modules in show_help only
        parser = argparse.ArgumentParser(
            formatter_class=type(
                "_HelpFormatter",
                (argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter),
                {},
            )
        )
        parser.print_usage = parser.print_help  # type: ignore
        return parser


class App(_Configurator):
    context_factory = Context

    @property
    def registry(self) -> Registry:
        return self.context.registry  # type: ignore

    @property
    def _aggressive_import_cache(self) -> t.Set[t.Union[str, t.Callable[..., None]]]:
        return self.context._aggressive_import_cache  # type: ignore

    @property
    def delayed_include_mapping(
        self,
    ) -> t.Dict[
        t.Callable[..., None],
        t.List[t.Tuple[App, t.Union[t.Callable[..., t.Any], str]]],
    ]:
        # TODO: fix memory leak
        return self.context._delayed_include_mapping  # type: ignore

    @property
    def cli_parser(self) -> ArgumentParser:
        return self.context.cli_parser  # type: ignore

    def include(
        self,
        fn_or_string: t.Union[t.Callable[..., t.Any], str],
        *,
        attrname: t.Optional[str] = None,
    ) -> t.Any:
        # more aggressive cache
        imported = self._aggressive_import_cache
        if fn_or_string in imported:
            return
        imported.add(fn_or_string)
        return super().include(fn_or_string, attrname=attrname)

    def include_when(
        self,
        fn_or_string: t.Union[t.Callable[..., t.Any], str],
        *,
        attrname: t.Optional[str] = None,
    ) -> t.Callable[[t.Callable[..., t.Any]], t.Callable[..., t.Any]]:
        def _register(command: t.Callable[..., t.Any]) -> t.Callable[..., t.Any]:
            self.delayed_include_mapping[command].append((self, fn_or_string))
            return command

        return _register

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
        self.registry.configure(dry_run=dry_run)
        runtime.set_context(runtime.RuntimeContext(self.registry, dry_run=dry_run))
        super().commit()

    def shallow_commit(self) -> None:
        super().commit()

    def run(self, argv: t.Optional[t.List[str]] = None) -> t.Any:
        from egoist.internal.logutil import logging_setup

        run_ = self.context.run  # type: ignore
        if run_ is not None:
            return run_(argv)

        activate = logging_setup(self.cli_parser)

        def _run(argv: t.Optional[t.List[str]] = None) -> t.Any:
            args = self.cli_parser.parse_args(argv)
            params = vars(args).copy()
            activate(params)
            subcommand = params.pop("subcommand", None)
            if subcommand is None:
                print(self.cli_parser.format_help())
                return
            return subcommand(**params)

        self.context.run = _run  # type:ignore
        return _run(argv)


def create_app(settings: SettingsDict) -> App:
    app = App(t.cast(t.Dict[str, t.Any], settings))
    app.include("egoist.commands.describe")
    app.include("egoist.commands.generate")
    app.include("egoist.commands.scan")
    return app


class SubApp:
    def __init__(self, *, name: str) -> None:
        self.name = name
        self.registered: t.List[
            t.Tuple[
                str,
                t.List[t.Tuple[t.Tuple[t.Any, ...], t.Dict[str, t.Any]]],
                t.Callable[..., t.Any],
            ]
        ] = []
        self.requires: t.Set[t.Union[str, t.Callable[..., t.Any]]] = set()
        self.callbacks: t.List[t.Callable[[App], t.Any]] = []

    def include(self, path: str) -> None:
        self.requires.add(path)

    def _append_include_when(
        self,
        app: App,
        *,
        command: t.Callable[..., t.Any],
        fn_or_string: t.Union[t.Callable[..., t.Any], str],
    ) -> None:
        app.delayed_include_mapping[command].append((app, fn_or_string))

    def include_when(
        self,
        fn_or_string: t.Union[t.Callable[..., t.Any], str],
        *,
        attrname: t.Optional[str] = None,
    ) -> t.Callable[[t.Callable[..., t.Any]], t.Callable[..., t.Any]]:
        def _register(command: t.Callable[..., t.Any]) -> t.Callable[..., t.Any]:
            self.callbacks.append(
                partial(
                    self._append_include_when,
                    command=command,
                    fn_or_string=fn_or_string,
                )
            )
            return command

        return _register

    def includeme(self, _app: App) -> None:
        import sys

        name = self.name
        module = sys.modules[name]
        app = _app.__class__(_app._settings, module=module, context=_app.context)

        seen = app.imported
        for path in self.requires:
            if path in seen:
                continue
            app.include(path)

        if len(self.callbacks) > 0:
            for cb in self.callbacks:
                cb(app)

        for name, buf, _ in self.registered:
            directive = getattr(app, name)
            for args, kwargs in buf:
                directive = directive(*args, **kwargs)

    # TODO: omit (temporary implementation for supporting directives)
    def __getattr__(self, name: str) -> t.Callable[..., AnyFunction]:
        def _register(
            *args: t.Any,
            _buf: t.Optional[
                t.List[t.Tuple[t.Tuple[t.Any, ...], t.Dict[str, t.Any]]]
            ] = None,
            **kwargs: t.Any,
        ) -> AnyFunction:
            if _buf is None:
                _buf = []
            _buf.append((args, kwargs))
            if args and callable(args[-1]):
                task: AnyFunction = args[-1]
                self.registered.append((name, _buf, task))
                return task
            return partial(_register, _buf=_buf)

        return _register


def create_subapp(*, _depth: int = 1) -> SubApp:
    import sys

    # black magic: register includeme automatically
    f = sys._getframe(_depth)
    subapp = SubApp(name=f.f_globals["__name__"])
    if "includeme" not in f.f_globals:
        f.f_globals["includeme"] = subapp.includeme
    return subapp


def parse_args(
    argv: t.Optional[t.List[str]] = None, *, sep: str = "-"
) -> t.Iterator[t.Optional[t.List[str]]]:
    """for bulk action"""
    import sys
    import itertools

    argv = argv or sys.argv[1:]
    if not argv:
        yield None
        return

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

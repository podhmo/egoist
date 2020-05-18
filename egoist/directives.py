import typing as t
from .app import App, _noop

AnyFunction = t.Callable[..., t.Any]
T = t.TypeVar("T")

_has_subparser = False


def add_subcommand(app: App) -> None:
    """register subcommands"""
    global _has_subparser
    if _has_subparser:
        return
    _has_subparser = True

    import argparse

    parser = app.cli_parser
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")
    subparsers.required = True

    def _add_subcommand(
        app: App,
        setup_parser: t.Callable[[App, argparse.ArgumentParser, AnyFunction], None],
        *,
        fn: AnyFunction,
    ) -> None:
        sub_parser = subparsers.add_parser(
            fn.__name__, help=fn.__doc__, formatter_class=parser.formatter_class
        )
        setup_parser(app, sub_parser, fn)

    app.add_directive("add_subcommand", _add_subcommand)


def define_cli(app: App) -> None:
    name = "define_cli"
    seen = False

    def _register_cli(app: App, kit: str) -> AnyFunction:
        nonlocal seen
        if not seen:
            seen = True

        def _register(fn: AnyFunction) -> AnyFunction:
            app.registry.generators[kit].append(fn)
            app.registry._task_list.append(fn.__name__)
            return fn

        return _register

    app.add_directive(name, _register_cli)

    def _include() -> None:
        nonlocal seen
        if seen:
            app.include("egoist.generators.clikit")

    # for conflict check
    app.action(name, _include)


def define_struct_set(app: App) -> None:
    name = "define_struct_set"
    seen = False

    def _register_struct_set(app: App, kit: str) -> AnyFunction:
        nonlocal seen
        if not seen:
            seen = True

        def _register(fn: AnyFunction) -> AnyFunction:
            app.registry.generators[kit].append(fn)
            app.registry._task_list.append(fn.__name__)
            return fn

        return _register

    app.add_directive(name, _register_struct_set)

    def _include() -> None:
        nonlocal seen
        if seen:
            app.include("egoist.generators.structkit")

    # for conflict check
    app.action(name, _include)


def define_file(app: App) -> None:
    name = "define_file"
    seen = False

    def _register_file(
        app: App, kit: str, *, rename: t.Optional[str] = None, suffix: str = "",
    ) -> AnyFunction:
        nonlocal seen
        if not seen:
            seen = True

        def _register(fn: AnyFunction) -> AnyFunction:
            if rename is not None:
                fn._rename = rename  # type: ignore
            elif suffix:
                fn._rename = f"{fn.__name__}{suffix}"  # type: ignore
            app.registry.generators[kit].append(fn)
            app.registry._task_list.append(fn.__name__)
            return fn

        return _register

    app.add_directive(name, _register_file)

    def _include() -> None:
        nonlocal seen
        if seen:
            app.include("egoist.generators.filekit")

    # for conflict check
    app.action(name, _include)


def define_dir(app: App) -> None:
    name = "define_dir"
    seen = False

    def _register_dir(
        app: App, kit: str, *, rename: t.Optional[str] = None
    ) -> AnyFunction:
        nonlocal seen
        if not seen:
            seen = True

        def _register(fn: AnyFunction) -> AnyFunction:
            if rename is not None:
                fn._rename = rename  # type: ignore
            app.registry.generators[kit].append(fn)
            app.registry._task_list.append(fn.__name__)
            return fn

        return _register

    app.add_directive(name, _register_dir)

    def _include() -> None:
        nonlocal seen
        if seen:
            app.include("egoist.generators.dirkit")

    # for conflict check
    app.action(name, _include)


def shared(app: App) -> None:
    name = "shared"

    def _register_shared(app: App, fn: t.Callable[..., T]) -> AnyFunction:
        from functools import partial
        from prestring.codeobject import Symbol

        name = f"{fn.__module__}:{fn.__name__}"
        app.register_factory(name, fn)
        app.register_dryurn_factory(name, partial(Symbol, name))

        def cached(*args: t.Any, **kwargs: t.Any) -> T:
            from egoist.runtime import get_component

            return t.cast(T, get_component(name, *args, **kwargs))

        return cached

    app.add_directive(name, _register_shared)

    # for conflict check
    app.action(name, _noop)

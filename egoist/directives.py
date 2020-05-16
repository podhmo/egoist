import typing as t
from .app import App, _noop

AnyFunction = t.Callable[..., t.Any]


def define_cli(app: App) -> None:
    name = "define_cli"
    seen = False

    def _register_cli(app: App, kit: str) -> AnyFunction:
        nonlocal seen
        if not seen:
            seen = True
            app.include("egoist.generators.clikit")

        def _register(fn: AnyFunction) -> AnyFunction:
            app.registry.generators[kit].append(fn)
            return fn

        return _register

    app.add_directive(name, _register_cli)

    # for conflict check
    app.action(name, _noop)


def define_struct_set(app: App) -> None:
    name = "define_struct_set"
    seen = False

    def _register_struct_set(app: App, kit: str) -> AnyFunction:
        nonlocal seen
        if not seen:
            seen = True
            app.include("egoist.generators.structkit")

        def _register(fn: AnyFunction) -> AnyFunction:
            app.registry.generators[kit].append(fn)
            return fn

        return _register

    app.add_directive(name, _register_struct_set)

    # for conflict check
    app.action(name, _noop)


def define_file(app: App) -> None:
    name = "define_file"
    seen = False

    def _register_file(
        app: App, kit: str, *, rename: t.Optional[str] = None, suffix: str = "",
    ) -> AnyFunction:
        nonlocal seen
        if not seen:
            seen = True
            app.include("egoist.generators.filekit")

        def _register(fn: AnyFunction) -> AnyFunction:
            if rename is not None:
                fn._rename = rename  # xxx
            elif suffix:
                fn._rename = f"{fn.__name__}{suffix}"
            app.registry.generators[kit].append(fn)
            return fn

        return _register

    app.add_directive(name, _register_file)

    # for conflict check
    app.action(name, _noop)


def define_dir(app: App) -> None:
    name = "define_dir"
    seen = False

    def _register_dir(
        app: App, kit: str, *, rename: t.Optional[str] = None
    ) -> AnyFunction:
        nonlocal seen
        if not seen:
            seen = True
            app.include("egoist.generators.dirkit")

        def _register(fn: AnyFunction) -> AnyFunction:
            if rename is not None:
                fn._rename = rename  # xxx
            app.registry.generators[kit].append(fn)
            return fn

        return _register

    app.add_directive(name, _register_dir)

    # for conflict check
    app.action(name, _noop)

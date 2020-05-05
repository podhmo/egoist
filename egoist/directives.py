import typing as t
from .app import App

AnyFunction = t.Callable[..., t.Any]


def define_cli(app: App):
    name = "define_cli"

    def _register_cli(app: App, kit: str) -> AnyFunction:
        def _register(fn: AnyFunction) -> AnyFunction:
            app.registry.generate_settings[kit].append(fn)
            return fn

        return _register

    app.add_directive(name, _register_cli)

    # for conflict check
    app.action(name, _noop)


def _noop() -> None:
    pass
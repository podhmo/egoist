import typing as t
from egoist.app import App
from egoist.types import AnyFunction


def define_something(app: App) -> None:
    import sys

    name = "define_something"
    seen = False

    print("** on decorator", file=sys.stderr)

    def _register_something(app: App, something: t.Any) -> AnyFunction:
        nonlocal seen
        if not seen:
            seen = True

        def _register() -> AnyFunction:
            name = something.__name__
            print("*** {name}, on register".format(name=name), file=sys.stderr)

        app.action((name, something.__name__), _register)
        return _register

    app.add_directive(name, _register_something)

    def _include() -> None:
        nonlocal seen
        if seen:
            print("** on include", file=sys.stderr)

    # for conflict check
    app.action(name, _include)

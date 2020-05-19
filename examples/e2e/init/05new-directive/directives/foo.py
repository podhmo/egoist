import typing as t
from egoist.app import App
from egoist.types import AnyFunction


def define_foo(app: App) -> None:
    import sys

    name = "define_foo"
    seen = False

    print("** on decorator", file=sys.stderr)

    def _register_foo(app: App, foo: t.Any) -> AnyFunction:
        nonlocal seen
        if not seen:
            seen = True

        def _register() -> AnyFunction:
            name = foo.__name__
            print("*** {name}, on register".format(name=name), file=sys.stderr)

        app.action((name, foo.__name__), _register)
        return _register

    app.add_directive(name, _register_foo)

    def _include() -> None:
        nonlocal seen
        if seen:
            print("** on include", file=sys.stderr)

    # for conflict check
    app.action(name, _include)

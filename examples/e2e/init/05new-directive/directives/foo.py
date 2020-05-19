import typing as t
from egoist.app import App
from egoist.types import AnyFunction

def define_foo(app: App) -> None:
    import sys

    name = "define_foo"
    seen = False

    print("** do something, on decorator", file=sys.stderr)

    def _register_foo(app: App, something: t.Any) -> AnyFunction:
        nonlocal seen
        if not seen:
            seen = True

        def _register(fn: AnyFunction) -> AnyFunction:
            print("do something, on register", file=sys.stderr)
            return fn

        return _register

    app.add_directive(name, _register_foo)

    def _include() -> None:
        nonlocal seen
        if seen:
            print("do something, on include", file=sys.stderr)

    # for conflict check
    app.action(name, _include)

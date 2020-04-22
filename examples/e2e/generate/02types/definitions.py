from gogen import runtime
from gogen import types


def hello(*, name: str = "world", age: types.uint, debug: types.bool) -> None:
    """hello message"""
    from gogen.generate import cli

    with runtime.generate(cli):
        runtime.printf("hello %s(%d)\n", name, age)


if __name__ == "__main__":
    runtime.main(name=__name__, here=__file__)

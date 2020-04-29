from egoist import runtime
from egoist import types


def hello(
    *, name: str = "world", age: types.uint, debug: types.bool, dur: types.duration
) -> None:
    """hello message"""
    from egoist.generate import cli

    with runtime.generate(cli):
        runtime.printf("hello %s(%d)\n", name, age)


if __name__ == "__main__":
    runtime.main(name=__name__, here=__file__, root="cmd")

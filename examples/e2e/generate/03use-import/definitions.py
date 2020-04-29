from egoist import runtime


def hello(*, name: str = "World") -> None:
    """hello message"""
    from egoist.generate import cli

    with runtime.generate(cli) as m:
        hello = m.import_("m/hello")
        m.stmt(hello.Hello(name))


if __name__ == "__main__":
    runtime.main(name=__name__, here=__file__, root="cmd")

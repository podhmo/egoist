from egoist import runtime


def hello(*, name: str = "World") -> None:
    """hello message"""
    from egoist.generate.clikit import clikit

    with runtime.generate(clikit) as m:
        hello = m.import_("m/hello")
        m.stmt(hello.Hello(name))


if __name__ == "__main__":
    runtime.main(name=__name__, here=__file__, root="cmd")

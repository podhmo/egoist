from egoist import runtime


def hello(*, name: str = "foo") -> None:
    """hello message"""
    from egoist.generate.clikit import clikit

    args = runtime.get_args()
    args.name.help = "name of person"

    with runtime.generate(clikit):
        runtime.printf("hello %s\n", name)


if __name__ == "__main__":
    runtime.main(name=__name__, here=__file__, root="cmd")

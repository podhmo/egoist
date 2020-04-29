from egoist import runtime


def hello(*, name: str = "foo") -> None:
    """hello message"""
    from egoist.generate import cli

    args = runtime.get_args()
    args.name.help = "name of person"

    with runtime.generate(cli):
        runtime.printf("hello %s\n", name)


if __name__ == "__main__":
    runtime.main(name=__name__, here=__file__, root="cmd")

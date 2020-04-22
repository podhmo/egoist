from gogen import runtime


def hello(*, name: str) -> None:
    """hello message"""
    from gogen.generate import cli

    args = runtime.get_args()
    args.name.help = "name of person"
    args.name.default = "foo"

    with runtime.generate(cli) as m:
        runtime.printf("hello %s\n", name)


if __name__ == "__main__":
    runtime.main(name=__name__, here=__file__)

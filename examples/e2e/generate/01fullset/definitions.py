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
    from gogen.cmdutil import as_subcommand, Config

    @as_subcommand
    def describe():
        from gogen.cli import describe

        describe(__name__)

    @as_subcommand
    def generate(*, root: str = "cmd"):
        from gogen.generate import generate_all
        import pathlib
        from gogen.scan import scan_module
        import sys

        rootdir = pathlib.Path(__file__).parent / root
        fns = scan_module(sys.modules[__name__])
        generate_all(fns, root=rootdir)

    as_subcommand.run(config=Config(ignore_expose=True))

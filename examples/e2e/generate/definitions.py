def hello(*, name: str) -> None:
    """hello message"""
    pass


if __name__ == "__main__":
    from gogen.cmdutil import as_subcommand, Config

    @as_subcommand
    def describe():
        from gogen.cli import describe

        describe(__name__)

    as_subcommand.run(config=Config(ignore_expose=True))

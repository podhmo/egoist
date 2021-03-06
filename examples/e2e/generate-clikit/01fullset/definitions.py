from egoist.app import create_app, SettingsDict, parse_args

settings: SettingsDict = {"rootdir": "cmd/", "here": __file__}
app = create_app(settings)

app.include("egoist.directives.define_cli")


@app.define_cli("egoist.generators.clikit:walk")
def hello(*, name: str = "foo") -> None:
    """hello message"""
    from egoist.generators.clikit import runtime, clikit

    options = runtime.get_cli_options()
    options.name.help = "name of person"

    with runtime.generate(clikit):
        runtime.printf("hello %s\n", name)


if __name__ == "__main__":
    for argv in parse_args(sep="-"):
        app.run(argv)

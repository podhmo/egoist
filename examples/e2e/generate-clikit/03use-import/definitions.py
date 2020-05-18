from egoist.app import create_app, SettingsDict, parse_args

settings: SettingsDict = {"rootdir": "", "here": __file__}
app = create_app(settings)

app.include("egoist.directives.define_cli")


@app.define_cli("egoist.generators.clikit:walk")
def cmd__hello(*, name: str = "World") -> None:
    """hello message"""
    from egoist.generators.clikit import runtime, clikit

    with runtime.generate(clikit) as m:
        hello = m.import_("m/hello")
        m.stmt(hello.Hello(name))


if __name__ == "__main__":
    for argv in parse_args(sep="-"):
        app.run(argv)

from egoist.app import App, SettingsDict

settings: SettingsDict = {"root": "cmd/", "here": __file__}
app = App(settings)

app.include("egoist.directives.define_cli")
define_cli = app.define_cli("egoist.generate:walk")


@define_cli
def hello(*, name: str = "World") -> None:
    """hello message"""
    from egoist import runtime
    from egoist.generate.clikit import clikit

    with runtime.generate(clikit) as m:
        hello = m.import_("m/hello")
        m.stmt(hello.Hello(name))


if __name__ == "__main__":
    app.run()

from egoist.app import App, SettingsDict

settings: SettingsDict = {"root": "cmd/", "here": __file__}
app = App(settings)

app.include("egoist.directives.define_cli")
define_cli = app.define_cli("egoist.generate:walk")


@define_cli
def hello(*, name: str) -> None:
    """hello message"""
    from egoist import runtime
    from egoist.generate.clikit import clikit

    with runtime.generate(clikit):
        runtime.printf("hello %s\n", name)


@define_cli
def byebye(*, name: str) -> None:
    """byebye message"""
    from egoist import runtime
    from egoist.generate.clikit import clikit

    with runtime.generate(clikit):
        runtime.printf("byebye %s\n", name)


if __name__ == "__main__":
    app.run()

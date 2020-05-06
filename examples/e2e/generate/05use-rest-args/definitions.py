from egoist.app import App, SettingsDict

settings: SettingsDict = {"root": "cmd/", "here": __file__}
app = App(settings)

app.include("egoist.directives.define_cli")


@app.define_cli("egoist.generate.clikit:walk")
def hello(*, name: str) -> None:
    """hello message"""
    from egoist.generate.clikit import runtime, clikit

    with runtime.generate(clikit) as m:
        args = runtime.get_cli_rest_args()
        target = m.symbol("target")
        with m.for_(f"_, {target} := range {args}"):
            runtime.printf("%s: hello %s\n", name, target)


if __name__ == "__main__":
    app.run()

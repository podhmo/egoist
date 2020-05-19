from egoist.app import App, SettingsDict, parse_args

settings: SettingsDict = {"rootdir": "cmd/", "here": __file__}
app = App(settings)
app.include("directives.foo:define_foo")


@app.define_foo
def xxx(app: App) -> None:
    pass


if __name__ == "__main__":
    for argv in parse_args(sep="-"):
        app.run(argv)

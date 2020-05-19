from egoist.app import App, SettingsDict, parse_args

settings: SettingsDict = {"rootdir": "cmd/", "here": __file__}
app = App(settings)
app.include("commands.foo")


if __name__ == "__main__":
    for argv in parse_args(sep="-"):
        app.run(argv)

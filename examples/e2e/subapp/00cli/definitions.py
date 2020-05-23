from egoist.app import create_app, SettingsDict, parse_args

settings: SettingsDict = {"rootdir": "cmd/", "here": __file__}
app = create_app(settings)

app.include("apps.hello")
app.include("apps.byebye")

if __name__ == "__main__":
    for argv in parse_args(sep="-"):
        app.run(argv)

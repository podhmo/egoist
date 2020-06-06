from egoist.app import create_app, SettingsDict, parse_args, App

settings: SettingsDict = {"rootdir": "output", "here": __file__}
app = create_app(settings)

app.include("egoist.directives.define_file")
app.include("egoist.directives.shared")


def xxx(app: App):
    print("INCLUDE", "xxx")
    app.registry.settings["xxx"] = "xxx"


def yyy(app: App):
    print("INCLUDE", "yyy")
    app.registry.settings["yyy"] = "yyy"


def zzz(app: App):
    print("INCLUDE", "zzz")
    app.registry.settings["zzz"] = "zzz"


@app.define_file("egoist.generators.filekit:walk", suffix=".txt")
@app.include_when(xxx)
@app.include_when(yyy)
def hello() -> None:
    from egoist.generators.filekit import runtime

    with runtime.create_file() as wf:
        print("hello world", file=wf)
        print(app.registry.settings.get("xxx", "-"), file=wf)
        print(app.registry.settings.get("yyy", "-"), file=wf)
        print(app.registry.settings.get("zzz", "-"), file=wf)


@app.define_file("egoist.generators.filekit:walk", suffix=".txt")
@app.include_when(xxx)
@app.include_when(zzz)
def byebye() -> None:
    from egoist.generators.filekit import runtime

    with runtime.create_file() as wf:
        print("byebye world", file=wf)
        print(app.registry.settings.get("xxx", "-"), file=wf)
        print(app.registry.settings.get("yyy", "-"), file=wf)
        print(app.registry.settings.get("zzz", "-"), file=wf)


if __name__ == "__main__":
    for argv in parse_args(sep="-"):
        app.run(argv)

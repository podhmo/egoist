from egoist.app import create_app, SettingsDict, parse_args

settings: SettingsDict = {"rootdir": "output", "here": __file__}
app = create_app(settings)

app.include("egoist.directives.define_file")


@app.define_file("egoist.generators.filekit:walk", suffix=".json")
def openapi() -> None:
    from egoist.generators.filekit import runtime
    from app import app
    from dictknife import loading
    from openapi.emit import emit

    with runtime.create_file() as wf:
        d = emit(list(app.routes), title="egoist", version="0.0.0")
        loading.dump(d, wf, format="json")


if __name__ == "__main__":
    for argv in parse_args(sep="-"):
        app.run(argv)

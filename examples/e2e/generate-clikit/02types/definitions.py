from egoist.app import App, SettingsDict
from egoist import types

settings: SettingsDict = {"rootdir": "cmd/", "here": __file__}
app = App(settings)

app.include("egoist.directives.define_cli")


@app.define_cli("egoist.generators.clikit:walk")
def hello(
    *, name: str = "world", age: types.uint, debug: types.bool, dur: types.duration
) -> None:
    """hello message"""
    from egoist.generators.clikit import runtime, clikit

    with runtime.generate(clikit):
        runtime.printf("hello %s(%d)\n", name, age)


if __name__ == "__main__":
    app.run()

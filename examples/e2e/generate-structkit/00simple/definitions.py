from egoist.app import App, SettingsDict

settings: SettingsDict = {"root": "", "here": __file__}
app = App(settings)

app.include("egoist.directives.define_struct_set")


class Person:
    name: str
    age: int


@app.define_struct_set("egoist.generate.structkit:walk")
def models__models() -> None:
    from egoist.generate.structkit import runtime, structkit

    with runtime.generate(structkit, classes=[Person]) as m:
        m.package("models")


if __name__ == "__main__":
    app.run()

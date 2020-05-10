import typing_extensions as tx
from egoist.app import App, SettingsDict

settings: SettingsDict = {"rootdir": "", "here": __file__}
app = App(settings)

app.include("egoist.directives.define_struct_set")

Op = tx.Literal["add", "sub", "mul"]
Op.__name__ = "Op"  # TODO: remove


@app.define_struct_set("egoist.generators.structkit:walk")
def models__models() -> None:
    from egoist.generators.structkit import runtime, structkit

    with runtime.generate(structkit, classes=[Op]) as m:
        m.package("models")


if __name__ == "__main__":
    app.run()

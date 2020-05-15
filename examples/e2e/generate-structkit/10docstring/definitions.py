from egoist.app import App, SettingsDict, parse_args
from egoist.generators.structkit.runtime import metadata, field


settings: SettingsDict = {"rootdir": "", "here": __file__}
app = App(settings)

app.include("egoist.directives.define_struct_set")


class Person:
    """
    person object

    - name
    - age
    """

    name: str = field(metadata=metadata(comment="name of person"))
    age: int = field(metadata=metadata(comment="age of person"))


@app.define_struct_set("egoist.generators.structkit:walk")
def models__models() -> None:
    from egoist.generators.structkit import runtime, structkit

    with runtime.generate(structkit, classes=[Person]) as m:
        m.package("models")


if __name__ == "__main__":
    for argv in parse_args(sep="-"):
        app.run(argv)

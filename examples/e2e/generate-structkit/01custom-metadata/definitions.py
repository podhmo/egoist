import typing as t
from egoist.app import App, SettingsDict

settings: SettingsDict = {"rootdir": "", "here": __file__}
app = App(settings)

app.include("egoist.directives.define_struct_set")


class Person:
    name: str
    age: int


@app.define_struct_set("egoist.generators.structkit:walk")
def models__models() -> None:
    from egoist.generators.structkit import runtime, structkit

    @runtime.set_metadata_handler
    def metadata_handler(
        cls: t.Type[t.Any], *, name: str, info: t.Any, metadata: runtime.Metadata
    ) -> None:
        """Yaml also added"""
        metadata["tags"] = {"json": [name.rstrip("_")], "yaml": [name.rstrip("_")]}

    with runtime.generate(structkit, classes=[Person]) as m:
        m.package("models")


if __name__ == "__main__":
    app.run()

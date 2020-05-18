from __future__ import annotations
import typing as t
from egoist.app import create_app, SettingsDict, parse_args

settings: SettingsDict = {"rootdir": "", "here": __file__}
app = create_app(settings)

app.include("egoist.directives.define_struct_set")


class Person:
    name: str
    age: int

    items: t.Dict[str, Item]
    items2: t.Dict[str, t.Optional[Item]]


class Item:
    name: str
    description: str
    effect: str


@app.define_struct_set("egoist.generators.structkit:walk")
def models__models() -> None:
    from egoist.generators.structkit import runtime, structkit

    with runtime.generate(structkit, classes=[Person]) as m:
        m.package("models")


if __name__ == "__main__":
    for argv in parse_args(sep="-"):
        app.run(argv)

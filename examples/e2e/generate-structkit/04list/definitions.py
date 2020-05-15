from __future__ import annotations
import typing as t
from egoist.app import App, SettingsDict, parse_args

settings: SettingsDict = {"rootdir": "", "here": __file__}
app = App(settings)

app.include("egoist.directives.define_struct_set")


class Person:
    name: str
    age: int

    parents: t.List[t.Optional[Person]]
    parents2: t.List[Person]

    children: t.Tuple[t.Optional[Person]]
    children2: t.Tuple[Person]


@app.define_struct_set("egoist.generators.structkit:walk")
def models__models() -> None:
    from egoist.generators.structkit import runtime, structkit

    with runtime.generate(structkit, classes=[Person]) as m:
        m.package("models")


if __name__ == "__main__":
    for argv in parse_args(sep="-"):
        app.run(argv)

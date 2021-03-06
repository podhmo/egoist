from __future__ import annotations
import typing as t
from egoist.app import create_app, SettingsDict, parse_args

settings: SettingsDict = {"rootdir": "", "here": __file__}
app = create_app(settings)

app.include("egoist.directives.define_struct_set")


class Person:
    name: str
    age: int

    followings: t.List[t.List[Person]]
    followings2: t.List[t.List[t.Optional[Person2]]]

    groups: t.Dict[str, t.Dict[str, Person]]
    groups2: t.Dict[str, t.Dict[str, t.Optional[Person2]]]


class Person2:
    name: str


@app.define_struct_set("egoist.generators.structkit:walk")
def models__models() -> None:
    from egoist.generators.structkit import runtime, structkit

    with runtime.generate(structkit, classes=[Person]) as m:
        m.package("models")


if __name__ == "__main__":
    for argv in parse_args(sep="-"):
        app.run(argv)

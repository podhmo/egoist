from __future__ import annotations
import typing as t
from egoist.app import App, SettingsDict
from egoist.go.types import gopackage


settings: SettingsDict = {"root": "", "here": __file__}
app = App(settings)

app.include("egoist.directives.define_struct_set")


class Person:
    name: str
    age: int
    memo: Memo
    memo2: t.Optional[Memo]
    memo_listmap: t.Dict[str, t.List[Memo]]


@gopackage("m/other")
class Memo:
    text: str


@app.define_struct_set("egoist.generators.structkit:walk")
def models__models() -> None:
    from egoist.generators.structkit import runtime, structkit

    with runtime.generate(structkit, classes=[Person]) as m:
        m.package("models")


if __name__ == "__main__":
    app.run()

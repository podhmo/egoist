from __future__ import annotations
import typing as t
from egoist.app import App, SettingsDict

settings: SettingsDict = {"root": "", "here": __file__}
app = App(settings)

app.include("egoist.directives.define_struct_set")


class Empty:
    pass


class Leaf:
    value: int


class Node:
    left: Tree
    right: Tree


Tree = t.Union[Empty, Leaf, Node]
Tree.__name__ = "Tree"


@app.define_struct_set("egoist.generators.structkit:walk")
def models__models() -> None:
    from egoist.generators.structkit import runtime, structkit

    with runtime.generate(structkit, classes=[Tree]) as m:
        m.package("models")


if __name__ == "__main__":
    app.run()

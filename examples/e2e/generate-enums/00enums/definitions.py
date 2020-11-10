from __future__ import annotations
import typing_extensions as tx
from egoist.app import App, SettingsDict
from egoist.typing import NewNamedType

settings: SettingsDict = {"rootdir": "", "here": __file__}
app = App(settings)

app.include("egoist.directives.define_struct_set")

WeekDay = NewNamedType(
    "WeekDay",
    tx.Literal[
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
    ],
)


@app.define_struct_set("egoist.generators.structkit:walk")
def enums__weekdays() -> None:
    from egoist.generators.structkit import runtime, structkit

    with runtime.generate(structkit, classes=[WeekDay]) as m:
        m.package("enums")


if __name__ == "__main__":
    app.run()

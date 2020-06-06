from egoist.app import create_subapp, App

app = create_subapp()

app.include("egoist.directives.define_file")


def yyy(app: App):
    print("INCLUDE", "yyy")
    app.registry.settings["yyy"] = "yyy"


def zzz(app: App):
    print("INCLUDE", "zzz")
    app.registry.settings["zzz"] = "zzz"


@app.define_file("egoist.generators.filekit:walk", suffix=".txt")
@app.include_when(".xxx")
@app.include_when(yyy)
def hello() -> None:
    from egoist.generators.filekit import runtime
    from egoist.runtime import get_current_context

    registry = get_current_context().registry

    with runtime.create_file() as wf:
        print("hello world", file=wf)
        print(registry.settings.get("xxx", "-"), file=wf)
        print(registry.settings.get("yyy", "-"), file=wf)


@app.define_file("egoist.generators.filekit:walk", suffix=".txt")
@app.include_when("foo.xxx")
@app.include_when(zzz)
def byebye() -> None:
    from egoist.generators.filekit import runtime
    from egoist.runtime import get_current_context

    registry = get_current_context().registry

    with runtime.create_file() as wf:
        print("byebye world", file=wf)
        print(registry.settings.get("xxx", "-"), file=wf)
        print(registry.settings.get("zzz", "-"), file=wf)

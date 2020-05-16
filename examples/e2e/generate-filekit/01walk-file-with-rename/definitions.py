from egoist.app import App, SettingsDict, parse_args

settings: SettingsDict = {"rootdir": "output", "here": __file__}
app = App(settings)

app.include("egoist.directives.define_file")


@app.define_file("egoist.generators.filekit:walk", rename="xxx/hello.txt")
def hello() -> None:
    from egoist.generators.filekit import runtime

    with runtime.create_file() as wf:
        print("hello world", file=wf)


@app.define_file("egoist.generators.filekit:walk", rename="xxx__byebye.txt")
def byebye() -> None:
    from egoist.generators.filekit import runtime

    with runtime.create_file() as wf:
        print("byebye world", file=wf)


if __name__ == "__main__":
    for argv in parse_args(sep="-"):
        app.run(argv)

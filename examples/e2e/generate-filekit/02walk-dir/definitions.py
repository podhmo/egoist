from egoist.app import App, SettingsDict, parse_args

settings: SettingsDict = {"rootdir": "output", "here": __file__}
app = App(settings)

app.include("egoist.directives.define_dir")


@app.define_dir("egoist.generators.dirkit:walk")
def data() -> None:
    from egoist.generators.dirkit import runtime

    with runtime.create_file("hello.txt"):
        print("hello world")

    with runtime.create_file("byebye.txt"):
        print("byebye world")


if __name__ == "__main__":
    for argv in parse_args(sep="-"):
        app.run(argv)

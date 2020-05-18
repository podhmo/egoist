from egoist.app import create_app, SettingsDict, parse_args

settings: SettingsDict = {"rootdir": "cmd/", "here": __file__}
app = create_app(settings)

app.include("egoist.directives.define_cli")


@app.define_cli("egoist.generators.clikit:walk")
def hello(*, name: str) -> None:
    """hello message"""
    from egoist.generators.clikit import runtime, clikit

    with runtime.generate(clikit) as m:
        args = runtime.get_cli_rest_args()
        target = m.symbol("target")
        with m.for_(f"_, {target} := range {args}"):
            runtime.printf("%s: hello %s\n", name, target)


if __name__ == "__main__":
    for argv in parse_args(sep="-"):
        app.run(argv)

from egoist.app import App, SettingsDict, parse_args

settings: SettingsDict = {"rootdir": "cmd/", "here": __file__}
app = App(settings)

app.include("egoist.directives.define_cli")


@app.define_cli("egoist.generators.clikit:walk")
def wire_example(*, grumby: bool = False) -> None:
    """
    google/wire event examples
    """
    from egoist.generators.clikit import runtime, clikit
    from egoist.go import di

    internal = app.maybe_dotted("internal")  # ./internal.py

    with runtime.generate(clikit) as m:
        b = di.Builder()

        # Greeter depends on Message
        # and, Event depends on Greeter
        b.add_provider(internal.NewMessage)
        b.add_provider(internal.NewGreeter)
        b.add_provider(internal.NewEvent)

        injector = b.build(variables=locals())
        event = injector.inject(m)
        m.stmt(event.Start())


if __name__ == "__main__":
    for argv in parse_args(sep="-"):
        app.run(argv)

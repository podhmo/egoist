from egoist.app import App, SettingsDict

settings: SettingsDict = {"root": "cmd/", "here": __file__}
app = App(settings)

app.include("egoist.directives.define_cli")


@app.define_cli("egoist.generate.clikit:walk")
def wire_example(*, grumby: bool = False) -> None:
    """
    google/wire event examples
    """
    from egoist.generate.clikit import runtime, clikit
    from egoist.go import di

    internal = app.maybe_dotted("internal")

    with runtime.generate(clikit) as m:
        b = di.Builder()

        b.add_provider(internal.NewMessage)
        b.add_provider(internal.NewGreeter)
        b.add_provider(internal.NewEvent)

        injector = b.build(variables=locals())
        event = injector.inject(m)
        m.stmt(event.Start())


if __name__ == "__main__":
    app.run()

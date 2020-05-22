from .subapp import SubApp
app = SubApp()


@app.define_cli("egoist.generators.clikit:walk")
def byebye(*, name: str) -> None:
    """byebye message"""
    from egoist.generators.clikit import runtime, clikit

    with runtime.generate(clikit):
        runtime.printf("byebye %s\n", name)


includeme = app.includeme

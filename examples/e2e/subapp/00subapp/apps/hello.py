from .subapp import SubApp
app = SubApp()


@app.define_cli("egoist.generators.clikit:walk")
def hello(*, name: str) -> None:
    """hello message"""
    from egoist.generators.clikit import runtime, clikit

    with runtime.generate(clikit):
        runtime.printf("hello %s\n", name)


includeme = app.includeme

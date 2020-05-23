from egoist.app import create_subapp

app = create_subapp()
app.include("egoist.directives.define_cli")


@app.define_cli("egoist.generators.clikit:walk")
def hello(*, name: str) -> None:
    """hello message"""
    from egoist.generators.clikit import runtime, clikit

    with runtime.generate(clikit):
        runtime.printf("hello %s\n", name)

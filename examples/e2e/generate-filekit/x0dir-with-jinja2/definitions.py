from egoist.app import App, SettingsDict, parse_args

settings: SettingsDict = {"rootdir": "", "here": __file__}
app = App(settings)

app.include("egoist.directives.define_dir")


@app.define_dir("egoist.generators.dirkit:walk")
def output(
    *, fizzbuzz_template="templates/fizzbuzz.j2", inputs_template="templates/inputs.j2",
) -> None:
    from egoist.generators.dirkit import runtime

    from jinja2 import Environment, FunctionLoader, StrictUndefined

    env = Environment(
        loader=FunctionLoader(lambda name: open(name).read()),
        undefined=StrictUndefined,
    )

    with runtime.create_file(f"fizzbuzz.txt", depends_on=[fizzbuzz_template]) as wf:
        t = env.get_template(str(fizzbuzz_template))
        print(t.render(n=30), file=wf)

    with runtime.create_file(f"inputs.html", depends_on=[inputs_template]) as wf:
        t = env.get_template(str(inputs_template))
        print(t.render(), file=wf)


if __name__ == "__main__":
    for argv in parse_args(sep="-"):
        app.run(argv)

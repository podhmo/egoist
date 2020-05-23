from egoist.app import create_subapp

app = create_subapp()

app.include("egoist.directives.define_dir")


@app.define_dir("egoist.generators.dirkit:walk", rename="output/byebye")
def output(*, source="input/byebye.tmpl") -> None:
    from egoist.generators.dirkit import runtime

    with open(source) as rf:
        template = rf.read()

    for name in ["foo", "bar", "boo"]:
        with runtime.create_file(f"{name}.json", depends_on=[source]) as wf:
            print(template.format(name=name), file=wf)

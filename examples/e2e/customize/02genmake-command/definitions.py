import typing as t
from egoist.app import create_app, SettingsDict, parse_args

settings: SettingsDict = {"rootdir": "", "here": __file__}
app = create_app(settings)


app.include("commands.genmake")
app.include("egoist.directives:define_dir")
app.include("egoist.directives:define_file")


@app.define_dir("egoist.generators.dirkit:walk", rename="output")
def x(
    *,
    gen_py: str = "_tools/gen.py",
    x_yaml_ja2: str = "_tools/x-yaml.j2",
    x_go_ja2: str = "_tools/x-go.j2",
    x_csv: str = "input/x.csv",
):
    from egoist.generators.dirkit import runtime

    inputs = [gen_py, x_yaml_ja2, x_csv]
    with runtime.create_file("x.yaml", depends_on=inputs) as wf:
        print(_gen(inputs), file=wf)

    inputs = [gen_py, x_go_ja2, x_csv]
    with runtime.create_file("x.go", depends_on=inputs) as wf:
        print(_gen(inputs), file=wf)


@app.define_file("egoist.generators.filekit:walk", rename="output/y.go")
def y_go(
    *,
    gen_py: str = "_tools/gen.py",
    y_go_ja2: str = "_tools/y-go.j2",
    root_yaml: str = "input/root.yaml",
):
    from egoist.generators.filekit import runtime

    with runtime.create_file() as wf:
        print(_gen([gen_py, y_go_ja2, root_yaml]), file=wf)


def _gen(files: t.List[str]) -> str:
    import pathlib

    return f"_tools/gen.py {[pathlib.Path(x).name for x in files]}"


if __name__ == "__main__":
    for argv in parse_args(sep="-"):
        app.run(argv)

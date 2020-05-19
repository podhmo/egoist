import typing as t
from egoist.app import create_app, SettingsDict, parse_args

settings: SettingsDict = {"rootdir": "", "here": __file__}
app = create_app(settings)

app.include("commands.genmake")
app.include("egoist.directives:define_dir")


@app.define_dir("egoist.generators.dirkit:walk")
def output(
    *,
    gen_py: str = "_tools/gen.py",
    # for x
    x_yaml_ja2: str = "_tools/x-yaml.j2",
    x_go_ja2: str = "_tools/x-go.j2",
    x_csv: str = "input/x.csv",
    # for y
    y_go_ja2: str = "_tools/y-go.j2",
    root_yaml: str = "input/root.yaml",
):
    from egoist.generators.dirkit import runtime

    with runtime.create_file("x.yaml", depends_on=[gen_py, x_yaml_ja2, x_csv]) as wf:
        print(_gen([gen_py, x_yaml_ja2, x_csv]), file=wf)
    with runtime.create_file("x.go", depends_on=[gen_py, x_go_ja2, x_csv]) as wf:
        print(_gen([gen_py, x_go_ja2, x_csv]), file=wf)

    with runtime.create_file("y.go", depends_on=[gen_py, y_go_ja2, root_yaml]) as wf:
        print(_gen([gen_py, y_go_ja2, root_yaml]), file=wf)


def _gen(files: t.List[str]) -> str:
    import pathlib

    return f"_tools/gen.py {[pathlib.Path(x).name for x in files]}"


if __name__ == "__main__":
    for argv in parse_args(sep="-"):
        app.run(argv)

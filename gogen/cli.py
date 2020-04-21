from handofcats import as_subcommand, Config


@as_subcommand
def init(*, root: str = "."):
    """scaffold"""
    import pathlib
    import shutil
    from importlib.util import find_spec

    spec = find_spec("gogen")
    dirpath = pathlib.Path(spec.submodule_search_locations[0]) / "data"

    src = dirpath / "definitions.py.tmpl"
    dst = pathlib.Path(root) / "definitions.py"
    shutil.copy(src, dst)


@as_subcommand
def describe(module_name: str) -> None:
    import inspect
    import json
    from importlib import import_module

    m = import_module(module_name)
    defs = {}
    for name, v in m.__dict__.items():
        if name.startswith("_"):
            continue
        if not callable(v):
            continue
        if getattr(v, "__module__", "") != m.__name__:
            continue

        defs[v.__name__] = inspect.getdoc(v).strip().split("\n", 1)[0]

    d = {"definitions": defs}
    print(json.dumps(d, indent=2, ensure_ascii=False))


def main():
    return as_subcommand.run(_force=True, config=Config(ignore_expose=True))

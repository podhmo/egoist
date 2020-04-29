from egoist.internal.cmdutil import as_subcommand, Config
from .scan import scan_module


@as_subcommand
def init(*, root: str = "."):
    """scaffold"""
    import pathlib
    import shutil
    from importlib.util import find_spec

    spec = find_spec("egoist")
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
    fns = scan_module(m)

    defs = {
        name: (inspect.getdoc(fn) or "").strip().split("\n", 1)[0]
        for name, fn in fns.items()
    }
    d = {"definitions": defs}
    print(json.dumps(d, indent=2, ensure_ascii=False))


def main():
    return as_subcommand.run(_force=True, config=Config(ignore_expose=True))

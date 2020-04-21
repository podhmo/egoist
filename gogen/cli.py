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


def main():
    return as_subcommand.run(_force=True, config=Config(ignore_expose=True))

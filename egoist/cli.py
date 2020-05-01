import typing as t
from .scan import scan_module


def init(*, root: str = ".") -> None:
    """scaffold"""
    import pathlib
    import shutil
    from importlib.util import find_spec

    spec = find_spec("egoist")
    if spec is None:
        return
    locations = spec.submodule_search_locations
    if locations is None:
        return
    dirpath = pathlib.Path(locations[0]) / "data"

    src = dirpath / "definitions.py.tmpl"
    dst = pathlib.Path(root) / "definitions.py"
    shutil.copy(src, dst)


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


def main(argv: t.Optional[t.List[str]] = None) -> t.Any:
    import argparse
    from egoist.internal.logutil import logging_setup

    parser = argparse.ArgumentParser(
        formatter_class=type(
            "_HelpFormatter",
            (argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter),
            {},
        )
    )
    parser.print_usage = parser.print_help  # type: ignore
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")
    subparsers.required = True

    fn = init
    sub_parser = subparsers.add_parser(
        fn.__name__, help=fn.__doc__, formatter_class=parser.formatter_class
    )
    sub_parser.add_argument("--root", required=False, default=".", help="-")
    sub_parser.set_defaults(subcommand=fn)

    fn = describe  # type: ignore
    sub_parser = subparsers.add_parser(
        fn.__name__, help=fn.__doc__, formatter_class=parser.formatter_class
    )
    sub_parser.add_argument("module_name", help="-")
    sub_parser.set_defaults(subcommand=fn)

    activate = logging_setup(parser)
    args = parser.parse_args(argv)
    params = vars(args).copy()
    activate(params)
    subcommand = params.pop("subcommand")
    return subcommand(**params)

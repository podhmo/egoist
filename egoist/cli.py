import typing as t


def init(*, target: str = "clikit", root: str = ".") -> None:
    """scaffold"""
    import logging
    import pathlib
    import shutil
    from importlib.util import find_spec

    logger = logging.getLogger(__name__)

    spec = find_spec("egoist")
    if spec is None:
        return
    locations = spec.submodule_search_locations
    if locations is None:
        return
    dirpath = pathlib.Path(locations[0]) / "data"

    src = dirpath / f"{target}_definitions.py.tmpl"
    dst = pathlib.Path(root) / "definitions.py"
    logger.info("create %s", dst)
    shutil.copy(src, dst)


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
    sub_parser.add_argument(
        "target", nargs="?", default="clikit", choices=["clikit", "structkit"]
    )
    sub_parser.set_defaults(subcommand=fn)

    activate = logging_setup(parser)
    args = parser.parse_args(argv)
    params = vars(args).copy()
    activate(params)
    subcommand = params.pop("subcommand")
    return subcommand(**params)

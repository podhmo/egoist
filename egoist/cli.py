import typing as t
import sys


def init(*, target: str = "clikit", root: str = ".") -> None:
    """scaffold"""
    import logging
    import pathlib
    import shutil
    from functools import partial
    from importlib.util import find_spec

    logger = logging.getLogger(__name__)

    spec = find_spec("egoist")
    if spec is None:
        return
    locations = spec.submodule_search_locations
    if locations is None:
        return
    dirpath = pathlib.Path(locations[0]) / "data"

    src = dirpath / f"{target}"
    dst = pathlib.Path(root)
    logger.info("create %s", dst)

    def _copy(src: str, dst: str) -> t.Any:
        if src.endswith(".tmpl"):
            dst = str(pathlib.Path(dst).with_suffix(""))
        return shutil.copy2(src, dst, follow_symlinks=True)

    if sys.version_info[:2] >= (3, 8):
        _copytree = partial(
            shutil.copytree, copy_function=_copy, symlinks=True, dirs_exist_ok=True
        )
    else:

        def _copytree(src: str, dst: str) -> t.Any:
            src_path = pathlib.Path(src)
            dst_path = pathlib.Path(dst)
            if src_path.is_dir():
                if not dst_path.exists():
                    return shutil.copytree(src, dst, symlinks=True, copy_function=_copy)
                for item in pathlib.Path(src).glob("*"):
                    if item.is_dir():
                        _copytree(str(item), str(dst_path / item.relative_to(src_path)))
                    else:
                        _copy(str(item), str(dst_path / item.relative_to(src_path)))
            else:
                _copy(src, dst)

    _copytree(str(src), str(dst))


def parse(
    *, filename: str, without_tab: bool = False, indent: t.Optional[int] = None
) -> None:
    """parse text"""
    from prestring.python.cli import run_transform
    from prestring.text.transform import transform
    from prestring.python import Module as PyModule
    from egoist.internal.prestringutil import Module

    m = run_transform(
        filename,
        transform=transform,
        name="emit",
        indent=(" " if without_tab else "\t") * (indent or 1),
        Module=PyModule,
        OutModule=Module,
    )
    print(m)


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

    # init
    fn = init
    sub_parser = subparsers.add_parser(
        fn.__name__, help=fn.__doc__, formatter_class=parser.formatter_class
    )
    sub_parser.add_argument("--root", required=False, default=".", help="-")
    sub_parser.add_argument(
        "target",
        nargs="?",
        default="clikit",
        choices=["clikit", "structkit", "filekit", "dirkit"],
    )
    sub_parser.set_defaults(subcommand=fn)

    # parse
    fn = parse
    sub_parser = subparsers.add_parser(
        fn.__name__, help=fn.__doc__, formatter_class=parser.formatter_class
    )
    sub_parser.add_argument("filename")
    sub_parser.add_argument("--without-tab", action="store_true")
    sub_parser.add_argument("--indent", default=None, type=int)
    sub_parser.set_defaults(subcommand=fn)

    activate = logging_setup(parser)
    args = parser.parse_args(argv)
    params = vars(args).copy()
    activate(params)
    subcommand = params.pop("subcommand")
    return subcommand(**params)

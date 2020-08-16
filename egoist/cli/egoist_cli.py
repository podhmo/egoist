from __future__ import annotations
import typing as t
import typing_extensions as tx
from magicalimport import import_module
from egoist.app import create_app, SettingsDict
from egoist.scan import scan_module


def run(
    filepath: str,
    *,
    rootdir: str = "cmd/",
    here: t.Optional[str] = None,
    action: tx.Literal["generate", "scan"] = "generate",
) -> None:
    m = import_module(filepath)
    here = here or m.__file__
    settings: SettingsDict = {"rootdir": rootdir, "here": here}
    app = create_app(settings)
    app.include("egoist.directives.define_cli")

    define_cli = app.define_cli("egoist.generators.clikit:walk")

    commands = scan_module(m)
    for name, fn in commands.items():
        define_cli(fn)
    app.run([action])


def main(argv: t.Optional[t.List[str]] = None) -> t.Any:
    import argparse

    parser = argparse.ArgumentParser(
        prog=run.__name__,
        description=run.__doc__,
        formatter_class=type(
            "_HelpFormatter",
            (argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter),
            {},
        ),
    )
    parser.print_usage = parser.print_help  # type: ignore
    parser.add_argument("filepath", help="-")
    parser.add_argument("--rootdir", required=False, default="cmd/", help="-")
    parser.add_argument("--here", required=False, help="-")
    parser.add_argument(
        "--action",
        required=False,
        default="generate",
        choices=["generate", "scan"],
        help="-",
    )
    args = parser.parse_args(argv)
    params = vars(args).copy()
    return run(**params)

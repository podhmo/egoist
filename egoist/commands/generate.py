from __future__ import annotations
import typing as t
from functools import partial
from miniconfig.exceptions import ConfigurationError
from egoist.app import App, get_root_path
from egoist.types import AnyFunction


def generate(
    app, *, targets: t.Optional[t.List[str]] = None, rootdir: t.Optional[str] = None,
) -> None:
    root_path = get_root_path(app.settings, root=rootdir)
    app.commit(dry_run=False)

    for kit, fns in app.registry.generators.items():
        walk_or_module = app.maybe_dotted(kit)
        if callable(walk_or_module):
            walk = walk_or_module
        elif hasattr(walk_or_module, "walk"):
            walk = walk_or_module.walk  # type: ignore
        else:
            # TODO: genetle error message
            raise ConfigurationError("{kit!r} is not callable")

        if not targets:
            sources = {fn.__name__: fn for fn in fns}
        else:
            sources = {fn.__name__: fn for fn in fns if fn.__name__ in targets}
        walk(sources, root=root_path)


def setup(app: App, sub_parser, fn: AnyFunction) -> None:
    target_choices = app.cli_targets  # ???

    sub_parser.add_argument("--rootdir", required=False, help="-")
    sub_parser.add_argument("targets", nargs="*", choices=[[]] + target_choices)  # type: ignore
    sub_parser.set_defaults(subcommand=partial(fn, app))


def includeme(app: App) -> None:
    app.add_subcommand(setup, fn=generate)

from __future__ import annotations
import typing as t
from functools import partial
from egoist.app import App
from egoist.types import AnyFunction

if t.TYPE_CHECKING:
    from argparse import ArgumentParser


def describe(app: App) -> None:
    import json
    import inspect
    from egoist.langhelpers import fullname

    app.commit(dry_run=False)

    defs = {}
    for kit, fns in app.registry.generators.items():
        for fn in fns:
            name = f"{fn.__module__}.{fn.__name__}".replace("__main__.", "")
            summary = (inspect.getdoc(fn) or "").strip().split("\n", 1)[0]
            defs[name] = {"doc": summary, "generator": kit}

    factories = {
        name: [fullname(x) for x in xs]  # type: ignore
        for name, xs in app.registry.factories.items()
    }
    d = {"definitions": defs, "factories": factories}
    print(json.dumps(d, indent=2, ensure_ascii=False))


def setup(app: App, sub_parser: ArgumentParser, fn: AnyFunction) -> None:
    sub_parser.set_defaults(subcommand=partial(fn, app))


def includeme(app: App) -> None:
    app.include("egoist.directives.add_subcommand")
    app.add_subcommand(setup, fn=describe)

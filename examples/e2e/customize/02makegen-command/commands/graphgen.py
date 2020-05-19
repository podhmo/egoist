from __future__ import annotations
import typing as t
import logging
from functools import partial
from egoist.app import App, get_root_path
from egoist.types import AnyFunction

if t.TYPE_CHECKING:
    from argparse import ArgumentParser


def graphgen(
    app: App,
    *,
    tasks: t.Optional[t.List[str]] = None,
    rootdir: t.Optional[str] = None,
    out: t.Optional[str] = None,
    relative: bool = True,
) -> None:
    import contextlib
    import os
    from egoist.components.tracker import get_tracker
    from egoist.commands.generate import generate

    app.commit(dry_run=True)

    if not bool(os.environ.get("VERBOSE", "")):
        logging.getLogger("prestring.output").setLevel(logging.WARNING)
    generate(app, tasks=tasks, rootdir=rootdir)

    root_path = get_root_path(app.settings, root=rootdir)
    deps_map = get_tracker().get_dependencies(root=root_path, relative=relative)

    with contextlib.ExitStack() as s:
        out_port: t.Optional[t.IO[str]] = None
        if out is not None:
            out_port = s.enter_context(open(out, "w"))
        print(emit(deps_map), file=out_port)


def emit(deps_map: t.Dict[str, t.List[str]]) -> str:
    from egoist.internal.graph import Builder
    from egoist.internal.graph import draw

    b = Builder()
    for name, deps in deps_map.items():
        b.add_node(deps["task"], depends=deps["depends"])
        b.add_node(name, depends=[deps["task"]])
    g = b.build()
    return draw.visualize(g, unique=True)


def setup(app: App, sub_parser: ArgumentParser, fn: AnyFunction) -> None:
    sub_parser.add_argument("--rootdir", required=False, help="-")
    sub_parser.add_argument("tasks", nargs="*", choices=app.registry._task_list)
    sub_parser.add_argument("--out")
    sub_parser.set_defaults(subcommand=partial(fn, app))


def includeme(app: App) -> None:
    app.include("egoist.components.tracker")
    app.include("egoist.directives.add_subcommand")
    app.include("egoist.commands.generate")
    app.add_subcommand(setup, fn=graphgen)

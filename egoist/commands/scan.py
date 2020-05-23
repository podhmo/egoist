from __future__ import annotations
import typing as t
import logging
from functools import partial
from egoist.app import App, get_root_path
from egoist.types import AnyFunction

if t.TYPE_CHECKING:
    from argparse import ArgumentParser
    from egoist.components.tracker import DependencyMap


def scan(
    app: App,
    *,
    tasks: t.Optional[t.List[str]] = None,
    rootdir: t.Optional[str] = None,
    out: t.Optional[str] = None,
    relative: bool = True,
    # for --rm
    rm: bool = False,
    # for --browse
    graph: bool = False,
    browse: bool = False,
) -> None:
    import contextlib
    import os
    from egoist.components.tracker import get_tracker
    from .generate import generate

    app.commit(dry_run=True)

    if not bool(os.environ.get("VERBOSE", "")):
        logging.getLogger("prestring.output").setLevel(logging.WARNING)
    generate(app, tasks=tasks, rootdir=rootdir)

    root_path = get_root_path(app.settings, root=rootdir)

    with contextlib.ExitStack() as s:
        out_port: t.Optional[t.IO[str]] = None

        if out is not None:
            out_port = s.enter_context(open(out, "w"))
        elif browse:
            import tempfile

            out_port = s.enter_context(
                tempfile.NamedTemporaryFile(mode="w+", delete=False)
            )

        deps = get_tracker().get_dependencies(root=root_path, relative=relative)
        if rm:
            _dump_as_rm_scripts(deps, output=out_port)
        elif graph:
            _dump_as_graph(deps, output=out_port, browse=browse)
        else:
            _dump_as_json(deps, output=out_port)


def _dump_as_rm_scripts(
    deps: DependencyMap, *, output: t.Optional[t.IO[str]] = None
) -> None:
    import sys
    from collections import defaultdict

    d = defaultdict(list)

    for fname, data in deps.items():
        d[data["task"]].append(fname)
    for task, fnames in d.items():
        print(f"# {task}", file=sys.stderr)
        for fname in fnames:
            print(f"rm {fname}", file=output)


def _dump_as_json(deps: DependencyMap, *, output: t.Optional[t.IO[str]] = None) -> None:
    import json

    print(json.dumps(deps, indent=2, ensure_ascii=False), file=output)


def _dump_as_graph(
    deps_map: DependencyMap,
    *,
    output: t.Optional[t.IO[str]] = None,
    browse: bool = False,
) -> None:
    from egoist.internal.graph import Builder
    from egoist.internal.graph import draw

    b = Builder()
    for name, deps in deps_map.items():
        b.add_node(deps["task"], depends=deps["depends"])  # type: ignore
        b.add_node(name, depends=[deps["task"]])  # type: ignore
    g = b.build()
    print(draw.visualize(g, unique=True), file=output)

    if browse:
        import atexit

        @atexit.register
        def callback() -> None:
            attrname = "name"
            if hasattr(output, attrname):
                import shutil
                import sys

                filename = getattr(output, attrname)
                print("write {}...".format(filename), file=sys.stderr)

                if shutil.which("dot"):
                    import subprocess

                    subprocess.run(["dot", "-Tsvg", "-O", filename], check=True)
                    # for mac
                    if shutil.which("open"):
                        subprocess.run(["open", "{}.svg".format(filename)])


def setup(app: App, sub_parser: ArgumentParser, fn: AnyFunction) -> None:
    sub_parser.add_argument("--rootdir", required=False, help="-")
    sub_parser.add_argument("tasks", nargs="*", choices=app.registry._task_list)
    sub_parser.add_argument("--out")

    sub_parser.add_argument("--rm", action="store_true")

    sub_parser.add_argument("--graph", action="store_true")
    sub_parser.add_argument("--browse", action="store_true")
    sub_parser.set_defaults(subcommand=partial(fn, app))


def includeme(app: App) -> None:
    app.include("egoist.directives.add_subcommand")
    app.include(".generate")
    app.add_subcommand(setup, fn=scan)

from __future__ import annotations
import typing as t
import logging
from functools import partial
from egoist.app import App, get_root_path
from egoist.types import AnyFunction

if t.TYPE_CHECKING:
    from argparse import ArgumentParser


def makegen(
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
    deps = get_tracker().get_dependencies(root=root_path, relative=relative)

    with contextlib.ExitStack() as s:
        out_port: t.Optional[t.IO[str]] = None
        if out is not None:
            out_port = s.enter_context(open(out, "w"))
        print(emit(deps), file=out_port)


def emit(deps: t.Dict[str, t.List[str]]) -> str:
    from prestring.text import Module

    deps = {
        name: {"task": x["task"], "depends": sorted(x["depends"])}
        for name, x in deps.items()
    }

    m = Module(indent="\t")
    m.stmt(f"DEP ?= {' '.join(deps.keys())}")
    m.stmt(f"PRE ?= {' '.join(['.pre/' + k.replace('/', '__') for k in deps.keys()])}")
    m.sep()
    m.stmt('CONT ?= PRE=$< DEP="" $(MAKE) _gen')
    m.stmt("BULK_ACTION = .pre/bulk.action")
    m.sep()

    m.stmt("# goal task")
    m.stmt("default:")
    with m.scope():
        m.stmt('@CONT="exit 0" $(MAKE) _gen')
    m.sep()

    m.stmt("_gen: .pre $(DEP)")
    with m.scope():
        m.stmt("@echo '**' $(PRE) '**' > /dev/stderr")
        m.stmt(
            "( $(foreach p,$(PRE),{ test $(p) -nt $(subst __,/,$(patsubst .pre/%,%,$(p))) && cat $(p); }; ) ) | sort | uniq > $(BULK_ACTION) || exit 0"
        )
        m.stmt(
            """test -n "$$(cat $(BULK_ACTION))" && NOCHECK=1 python definitions.py $$(cat $(BULK_ACTION) | tr '\\n' ' ') || exit 0"""
        )
    m.sep()

    m.stmt("# .pre files (sentinel)")
    for name, metadata in deps.items():
        task = metadata["task"]
        args = metadata["depends"]
        pre_file = f".pre/{name.replace('/', '__')}"
        m.stmt(f"{pre_file}: {' '.join(args)}")
        with m.scope():
            m.stmt(f'echo "generate {task} -" > $@')
    m.sep()

    m.stmt("# actual dependencies")
    for name, metadata in deps.items():
        task = metadata["task"]
        args = metadata["depends"]
        pre_file = f".pre/{name.replace('/', '__')}"
        m.stmt(f"{name}: {pre_file}")
        with m.scope():
            m.stmt(f"@$(CONT)")

    m.sep()
    m.stmt(".pre:")
    with m.scope():
        m.stmt("mkdir -p $@")
    return str(m)


def setup(app: App, sub_parser: ArgumentParser, fn: AnyFunction) -> None:
    sub_parser.add_argument("--rootdir", required=False, help="-")
    sub_parser.add_argument("tasks", nargs="*", choices=app.registry._task_list)
    sub_parser.add_argument("--out")
    sub_parser.set_defaults(subcommand=partial(fn, app))


def includeme(app: App) -> None:
    app.include("egoist.components.tracker")
    app.include("egoist.directives.add_subcommand")
    app.include("egoist.commands.generate")
    app.add_subcommand(setup, fn=makegen)

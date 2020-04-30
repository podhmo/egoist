from __future__ import annotations
import typing as t
import dataclasses

from .langhelpers import reify
from .types import Command
from .internal.prestringutil import Module
from .internal.prestringutil import goname, Symbol


class RuntimeContext:
    stack: t.List[Env]

    def __init__(self) -> None:
        self.stack = []


_REST_ARGS_NAME = "args"


class ArgsAttr:
    def __init__(self, names: t.List[str]):
        assert _REST_ARGS_NAME not in names
        self.data = {name: Arg(name=name) for name in names}

    def __getattr__(self, name: str) -> Arg:
        try:
            return self.data[name]
        except KeyError:
            raise AttributeError(name)


@dataclasses.dataclass
class Arg:
    name: str
    short_name: t.Optional[str] = None
    help: t.Optional[str] = None
    default: t.Optional[t.Any] = None


@dataclasses.dataclass
class Env:
    m: Module
    fn: Command
    prefix: str

    @reify
    def fnspec(self):
        from .internal._fnspec import fnspec

        return fnspec(self.fn)

    @reify
    def args(self) -> ArgsAttr:
        attr = ArgsAttr([name for name, _, _ in self.fnspec.parameters])
        for name, _, _ in self.fnspec.parameters:
            default = self.fnspec.default_of(name)
            if default is not None:
                getattr(attr, name).default = default
        return attr


_context = None


def printf(fmt_str: str, *args: t.Any) -> None:
    from prestring.utils import UnRepr
    import json

    m = get_self().stack[-1].m
    fmt = m.import_("fmt")
    # fixme: remove Unrepr and json.dumps
    m.stmt(fmt.Printf(UnRepr(json.dumps(fmt_str)), *args))


def generate(visit: t.Callable[[Env], t.ContextManager[None]]):
    c = get_self()
    env = c.stack[-1]
    return visit(env)


def get_cli_options() -> ArgsAttr:
    return get_self().stack[-1].args


def get_cli_rest_args() -> Symbol:
    prefix = get_self().stack[-1].prefix
    name = _REST_ARGS_NAME
    return Symbol(f"{prefix}.{goname(name)}")


def get_self() -> RuntimeContext:
    global _context
    if _context is None:
        set_self(RuntimeContext())
    return _context


def set_self(c: RuntimeContext) -> None:
    global _context
    _context = c


def main(*, name: str, here: str, root: str = "") -> None:
    from egoist.internal.cmdutil import as_subcommand, Config

    @as_subcommand
    def describe():
        from egoist.cli import describe

        describe(name)

    @as_subcommand
    def generate(*, root: str = root):
        import sys
        import pathlib
        from egoist.generate import walk
        from egoist.scan import scan_module

        rootdir = pathlib.Path(here).parent / root
        fns = scan_module(sys.modules[name])
        walk(fns, root=rootdir)

    as_subcommand.run(config=Config(ignore_expose=True), _force=True)

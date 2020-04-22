from __future__ import annotations
import typing as t
import dataclasses
from prestring.go import Module
from .langhelpers import reify
from .types import Command


class RuntimeContext:
    stack: t.List[Env]

    def __init__(self) -> None:
        self.stack = []


class ArgsAttr:
    def __init__(self, names: t.List[str]):
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

    @reify
    def fnspec(self):
        from ._fnspec import fnspec

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


def printf(fmt: str, *args: t.Any) -> None:
    from prestring.utils import LazyArguments, UnRepr
    import json

    m = get_self().stack[-1].m
    m.import_("fmt")  # TODO: return symbol
    m.append("fmt.Printf(")
    m.append(LazyArguments([UnRepr(json.dumps(fmt)), *args]))
    m.stmt(")")


def generate(generate_fn):
    c = get_self()
    env = c.stack[-1]
    return generate_fn(env)


def get_args() -> ArgsAttr:
    return get_self().stack[-1].args


def get_self() -> RuntimeContext:
    global _context
    if _context is None:
        set_self(RuntimeContext())
    return _context


def set_self(c: RuntimeContext) -> None:
    global _context
    _context = c


def main(*, name: str, here: str, root: str = "") -> None:
    from gogen.cmdutil import as_subcommand, Config

    @as_subcommand
    def describe():
        from gogen.cli import describe

        describe(name)

    @as_subcommand
    def generate(*, root: str = root):
        import sys
        import pathlib
        from gogen.generate import generate_all
        from gogen.scan import scan_module

        rootdir = pathlib.Path(here).parent / root
        fns = scan_module(sys.modules[name])
        generate_all(fns, root=rootdir)

    as_subcommand.run(config=Config(ignore_expose=True), _force=True)

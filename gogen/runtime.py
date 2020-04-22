from __future__ import annotations
import typing as t
import dataclasses
from prestring.go import Module
from .langhelpers import reify
from .types import Command


class RuntimeContext:
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
        return ArgsAttr([name for name, _, _ in self.fnspec.parameters])


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

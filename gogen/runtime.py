import typing as t
import dataclasses
from prestring.go import Module
from .langhelpers import reify
from .types import Command


class RuntimeContext:
    def __init__(self) -> None:
        self.stack = []


class Attr:
    def __init__(self, d: t.Dict[str, t.Any]) -> None:
        self.__dict__.update(d)


@dataclasses.dataclass
class Env:
    m: Module
    fn: Command

    @reify
    def fnspec(self):
        from ._fnspec import fnspec

        return fnspec(self.fn)


_context = None


def printf(fmt: str, *args: t.Any) -> None:
    from prestring.utils import LazyArguments, UnRepr
    import json

    m = get_self().stack[-1].m
    m.import_("fmt")  # TODO: return symbol
    m.append("fmt.Printf(")
    m.append(LazyArguments([UnRepr(json.dumps(fmt)), *args]))
    m.stmt(")")


def get_args() -> Attr:
    return get_self().stack[-1].args


def get_self() -> RuntimeContext:
    global _context
    if _context is None:
        set_self(RuntimeContext())
    return _context


def set_self(c: RuntimeContext) -> None:
    global _context
    _context = c

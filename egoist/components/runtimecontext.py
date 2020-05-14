from __future__ import annotations
import typing as t
import dataclasses

from egoist.langhelpers import reify
from egoist import types

if t.TYPE_CHECKING:
    from egoist.internal.prestringutil import Module
    from egoist.internal._fnspec import Fnspec


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
    fn: types.Command

    @reify
    def fnspec(self) -> Fnspec:
        from egoist.internal._fnspec import fnspec

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


def get_self() -> RuntimeContext:
    global _context
    if _context is None:
        set_self(RuntimeContext())
    assert _context is not None
    return _context


def set_self(c: RuntimeContext) -> None:
    global _context
    _context = c
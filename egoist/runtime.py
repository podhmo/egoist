from __future__ import annotations
import typing as t
import dataclasses

from . import types
from .langhelpers import reify
from .registry import get_global_registry

if t.TYPE_CHECKING:
    from egoist.internal.prestringutil import Module
    from egoist.internal._fnspec import Fnspec


class RuntimeContext:
    stack: t.List[Env]
    _component_instances: t.Dict[str, object]

    def __init__(self) -> None:
        self.stack = []
        self._component_instances = {}


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


def get_current_context() -> RuntimeContext:
    global _context
    if _context is None:
        set_context(RuntimeContext())
    assert _context is not None
    return _context


def set_context(c: RuntimeContext) -> None:
    global _context
    _context = c


def get_component_factory(name: str) -> types.ComponentFactory:
    return get_global_registry().factories[name][0]


def get_component(name: str, *args: t.Any, **kwargs: t.Any) -> object:
    c = get_current_context()
    ob = c._component_instances.get(name)
    if ob is not None:
        return ob

    factory = get_component_factory(name)
    ob = c._component_instances[name] = factory(*args, **kwargs)
    return ob


def printf(fmt_str: str, *args: t.Any) -> None:
    from prestring.utils import UnRepr
    import json

    m = get_current_context().stack[-1].m
    fmt = m.import_("fmt")
    # fixme: remove Unrepr and json.dumps
    m.stmt(fmt.Printf(UnRepr(json.dumps(fmt_str)), *args))

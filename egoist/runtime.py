from __future__ import annotations
import typing as t
from egoist.components.runtimecontext import RuntimeContext, Env, get_self, set_self
from .registry import get_global_registry

__all__ = [
    "RuntimeContext",
    "Env",
    "get_self",
    "set_self",
    # defined in this module
    "printf",
    "get_component",
]


def printf(fmt_str: str, *args: t.Any) -> None:
    from prestring.utils import UnRepr
    import json

    m = get_self().stack[-1].m
    fmt = m.import_("fmt")
    # fixme: remove Unrepr and json.dumps
    m.stmt(fmt.Printf(UnRepr(json.dumps(fmt_str)), *args))


def get_component(name: str) -> object:
    return get_global_registry().components[name][0]

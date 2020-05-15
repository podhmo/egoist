from __future__ import annotations
import typing as t
from egoist.runtime import get_self, printf, Env, ArgsAttr
from egoist.internal.prestringutil import goname, Symbol, Module

__all__ = [
    "get_self",
    "printf",
    "Env",
    # defined in this module
    "generate",
    "get_cli_options",
    "get_cli_rest_args",
]


def generate(
    visit: t.Callable[[Env], t.ContextManager[Module]]
) -> t.ContextManager[t.Any]:
    c = get_self()
    env = c.stack[-1]
    return visit(env)


def get_cli_options() -> ArgsAttr:
    return get_self().stack[-1].args


_PREFIX_DEFAULT = "opt"


def get_cli_rest_args(*, prefix: str = _PREFIX_DEFAULT) -> Symbol:
    from egoist.components.runtimecontext import _REST_ARGS_NAME

    name = _REST_ARGS_NAME
    return Symbol(f"{prefix}.{goname(name)}")

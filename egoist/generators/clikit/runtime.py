from __future__ import annotations
import typing as t
from egoist.runtime import get_current_context, printf, Env, ArgsAttr
from egoist.internal.prestringutil import goname, Symbol, Module
from . import _PREFIX_DEFAULT

__all__ = [
    "get_current_context",
    "printf",
    "Env",
    # defined in this module
    "generate",
    "get_cli_options",
    "get_cli_rest_args",
]


def generate(
    visit: t.Callable[[Env, bool], t.ContextManager[Module]]
) -> t.ContextManager[t.Any]:
    c = get_current_context()
    env = c.stack[-1]
    return visit(env, c.dry_run)


def get_cli_options() -> ArgsAttr:
    return get_current_context().stack[-1].args


def get_cli_rest_args(*, prefix: str = _PREFIX_DEFAULT) -> Symbol:
    from egoist.runtime import _REST_ARGS_NAME

    name = _REST_ARGS_NAME
    return Symbol(f"{prefix}.{goname(name)}")

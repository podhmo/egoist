from egoist.runtime import ArgsAttr, _REST_ARGS_NAME
from egoist.runtime import get_self, generate, printf, Env
from egoist.internal.prestringutil import goname, Symbol

__all__ = [
    "get_self",
    "generate",
    "printf",
    "Env",
    # defined in this module
    "get_cli_options",
    "get_cli_rest_args",
]


def get_cli_options() -> ArgsAttr:
    return get_self().stack[-1].args


def get_cli_rest_args() -> Symbol:
    prefix = get_self().stack[-1].prefix
    name = _REST_ARGS_NAME
    return Symbol(f"{prefix}.{goname(name)}")

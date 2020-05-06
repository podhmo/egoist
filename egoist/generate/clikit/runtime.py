from egoist.runtime import ArgsAttr, _REST_ARGS_NAME
from egoist.runtime import get_self, generate, printf, Env  # noqa: F401
from egoist.internal.prestringutil import goname, Symbol


def get_cli_options() -> ArgsAttr:
    return get_self().stack[-1].args


def get_cli_rest_args() -> Symbol:
    prefix = get_self().stack[-1].prefix
    name = _REST_ARGS_NAME
    return Symbol(f"{prefix}.{goname(name)}")

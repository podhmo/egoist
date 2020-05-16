import typing as t
import contextlib
from egoist.runtime import Env, get_current_context


def open() -> t.IO[str]:
    c = get_current_context()
    env = c.stack[-1]
    return contextlib.redirect_stdout(env.m)


__all__ = ["Env", "get_current_context"]

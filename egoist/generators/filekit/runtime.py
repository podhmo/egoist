import typing as t
import contextlib
from egoist.runtime import Env, get_current_context

__all__ = [
    "get_current_context",
    "Env",
    # defined in this module
    "create_file",
]


@contextlib.contextmanager
def create_file() -> t.Iterator[t.IO[str]]:
    c = get_current_context()
    env = c.stack[-1]
    yield env.io

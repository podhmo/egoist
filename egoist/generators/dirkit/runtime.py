import typing as t

import pathlib
import contextlib
from io import StringIO
from egoist.runtime import Env, get_current_context

__all__ = [
    "get_current_context",
    "Env",
    # defined in this module
    "create_file",
]

# TODO: depends_on
@contextlib.contextmanager
def create_file(filename: str) -> t.IO[str]:
    c = get_current_context()
    _env = c.stack[-1]
    fpath = str(pathlib.Path(_env.fpath) / filename)
    with _env.fs.open_file_with_tracking(
        fpath, "w", target=create_file, opener=StringIO
    ) as env:
        yield env.m

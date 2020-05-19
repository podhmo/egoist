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


@contextlib.contextmanager
def create_file(
    filename: str, *, depends_on: t.Optional[t.List[str]] = None
) -> t.Iterator[t.IO[str]]:
    c = get_current_context()
    _env = c.stack[-1]
    with _env.fs.open_file_with_tracking(
        pathlib.Path(_env.fpath) / filename,
        "w",
        target=_env.fn,
        opener=StringIO,
        depends_on=depends_on,
    ) as env:
        yield env.io

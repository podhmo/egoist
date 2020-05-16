from __future__ import annotations
import typing as t

import logging
import pathlib
from io import StringIO
from egoist import types
from egoist.components.fs import open_fs
from egoist.langhelpers import get_path_from_function_name

logger = logging.getLogger(__name__)


if t.TYPE_CHECKING:
    from egoist.app import App


def includeme(app: App):
    app.include("egoist.components.fs")


def walk(fns: t.Dict[str, types.Command], *, root: t.Union[str, pathlib.Path]) -> None:
    with open_fs(root=root) as fs:
        for name, fn in fns.items():
            logger.debug("walk %s", name)
            fpath = get_path_from_function_name(getattr(fn, "_rename", None) or name)
            with fs.open_file_with_tracking(fpath, "w", target=fn, opener=StringIO):
                fn()

from __future__ import annotations
import typing as t

import logging
import pathlib
from io import StringIO
from egoist.app import App
from egoist import types
from egoist.langhelpers import get_path_from_function_name

logger = logging.getLogger(__name__)


def walk(fns: t.Dict[str, types.Command], *, root: t.Union[str, pathlib.Path]) -> None:
    from egoist.components.tracker import get_tracker
    from egoist.components.fs import open_fs

    with open_fs(root=root) as fs:
        for name, fn in fns.items():
            logger.debug("walk %s", name)

            fpath = get_path_from_function_name(getattr(fn, "_rename", None) or name)
            with fs.open_file_with_tracking(
                fpath, "w", target=fn, opener=StringIO
            ) as env:
                kwargs = {
                    name: env.fnspec.here.parent / default
                    for name, default in (
                        env.fnspec.argspec.kwonlydefaults or {}
                    ).items()
                }
                get_tracker().track(fpath, task=fn, depends_on=kwargs.values())
                fn(**kwargs)


def includeme(app: App) -> None:
    app.include("egoist.components.tracker")
    app.include("egoist.components.fs")

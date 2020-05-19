from __future__ import annotations
import typing as t
import typing_extensions as tx

import pathlib
import os
from egoist.app import App
from egoist import runtime
from egoist import types


NAME = __name__

if t.TYPE_CHECKING:
    from egoist.internal.prestringutil import Module

    Content = t.Union[str, Module, t.IO[str]]
else:
    Content = t.Union[str, "Module", t.IO[str]]

T_co = t.TypeVar("T_co", covariant=True)
T = t.TypeVar("T", bound=Content)
Mode = tx.Literal["w"]  # support only "w", yet


class FSFactory(tx.Protocol):
    def __call__(self, *, root: t.Union[str, pathlib.Path]) -> t.ContextManager[FS]:
        ...


class FS(tx.Protocol):
    def open(
        self, filename: t.Union[str, pathlib.Path], mode: str
    ) -> t.ContextManager[Content]:
        ...

    def open_file_with_tracking(
        self,
        filename: t.Union[str, pathlib.Path],
        mode: str,
        *,
        target: types.Command,
        opener: t.Optional[t.Callable[[], T]] = None,
    ) -> t.ContextManager[runtime.Env]:
        ...

    def open_dir_with_tracking(
        self, filename: t.Union[str, pathlib.Path], *, target: types.Command,
    ) -> t.ContextManager[runtime.Env]:
        ...


def open_fs(*, root: t.Union[str, pathlib.Path]) -> t.ContextManager[FS]:
    factory = t.cast(FSFactory, runtime.get_component_factory(NAME))
    return factory(root=root)


def create_fs(*, root: t.Union[pathlib.Path, str]) -> t.ContextManager[FS]:
    """actual component"""
    from egoist.internal.prestringutil import Module
    from .fs_tracked_ import _TrackedOutput

    if "VERBOSE" in os.environ:
        verbose = bool(os.environ["VERBOSE"])
    else:
        verbose = True
    if "NOCHECK" in os.environ:
        nocheck = bool(os.environ["NOCHECK"])
    else:
        nocheck = False
    return _TrackedOutput(
        root=str(root), opener=Module, verbose=verbose, nocheck=nocheck
    )


def create_dummy_fs(*, root: t.Union[pathlib.Path, str]) -> t.ContextManager[FS]:
    """dry-run component"""
    from egoist.internal.prestringutil import Module
    from .fs_tracked_ import _TrackedOutput

    if "VERBOSE" in os.environ:
        verbose = bool(os.environ["VERBOSE"])
    else:
        verbose = False
    return _TrackedOutput(
        root=str(root), opener=Module, verbose=verbose, use_console=True, nocheck=False
    )


def includeme(app: App) -> None:
    app.include(".tracker")

    actual: FSFactory = create_fs
    app.register_factory(NAME, actual)

    for_dry_run: FSFactory = create_dummy_fs
    app.register_dryurn_factory(NAME, for_dry_run)

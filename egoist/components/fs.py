from __future__ import annotations
import typing as t
import typing_extensions as tx

import pathlib
from egoist.app import App
from egoist import runtime


if t.TYPE_CHECKING:
    from egoist.internal.prestringutil import Module

T_co = t.TypeVar("T_co", covariant=True)
NAME = __name__

Mode = tx.Literal["w"]  # support only "w", yet


class FSFactory(tx.Protocol[T_co]):
    def __call__(
        self, *, root: t.Union[str, pathlib.Path]
    ) -> t.ContextManager[FS[T_co]]:
        ...


class FS(tx.Protocol[T_co]):
    def open(
        self, filename: t.Union[str, pathlib.Path], mode: str
    ) -> t.ContextManager[T_co]:
        ...

    def open_with_tracking(
        self, filename: t.Union[str, pathlib.Path], mode: str, *, target: object
    ) -> t.ContextManager[runtime.Env]:
        ...


def open_fs(*, root: t.Union[str, pathlib.Path]) -> t.ContextManager[FS[Module]]:
    from egoist.internal.prestringutil import Module

    factory = t.cast(FSFactory[Module], runtime.get_component(NAME))
    return factory(root=root)


def create_fs(*, root: t.Union[pathlib.Path, str]) -> t.ContextManager[FS[Module]]:
    """actual component"""
    from egoist.internal.prestringutil import Module
    from .fs_tracked_ import _TrackedOutput

    return _TrackedOutput(root=str(root), opener=Module, verbose=True)


def create_dummy_fs(
    *, root: t.Union[pathlib.Path, str]
) -> t.ContextManager[FS[Module]]:
    """dry-run component"""
    from egoist.internal.prestringutil import Module
    from .fs_tracked_ import _TrackedOutput

    return _TrackedOutput(
        root=str(root), opener=Module, verbose=False, use_console=True, nocheck=False
    )


def includeme(app: App) -> None:
    actual: FSFactory[Module] = create_fs
    app.register_component(NAME, actual)

    for_dry_run: FSFactory[Module] = create_dummy_fs
    app.register_dryurn_component(NAME, for_dry_run)

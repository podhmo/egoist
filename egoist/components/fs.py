from __future__ import annotations
import typing as t
import typing_extensions as tx
import pathlib
from egoist.app import App
from egoist import runtime
from egoist import types


NAME = "fs_factory"
if t.TYPE_CHECKING:
    from egoist.internal.prestringutil import Module, output


class FSFactory(tx.Protocol):
    def __call__(self, *, root: t.Union[str, pathlib.Path]) -> output[Module]:
        ...


def open_fs(*, root: t.Union[str, pathlib.Path]) -> output[Module]:
    factory = runtime.get_component(NAME)
    return factory(root=root)  # type: ignore


def create_fs(*, root: t.Union[pathlib.Path, str]) -> output[Module]:
    """actual component"""
    from egoist.internal.prestringutil import output, Module

    return output(root=str(root), opener=Module, verbose=True)


def create_dummy_fs(*, root: t.Union[pathlib.Path, str]) -> output[Module]:
    """dry-run component"""
    from egoist.internal.prestringutil import output, Module

    return output(root=str(root), opener=Module, verbose=True, use_console=True)


def includeme(app: App) -> None:
    actual: FSFactory = create_fs
    app.register_component(NAME, actual)

    for_dry_run: FSFactory = create_dummy_fs
    app.register_component(NAME, for_dry_run, type_=types.DRYRUN_COMPONENT)

from __future__ import annotations
import typing as t
import pathlib
from egoist.app import App
from egoist.runtime import get_components


NAME = "fs_factory"
if t.TYPE_CHECKING:
    from egoist.internal.prestringutil import Module, output


def open_fs(*, root: t.Union[str, pathlib.Path]) -> output[Module]:
    return get_components(NAME)  # type: ignore


def create_fs(self: t.Any, *, root: t.Union[pathlib.Path, str]) -> output[Module]:
    """actual component"""
    from egoist.internal.prestringutil import output, Module

    return output(root=str(root), opener=Module, verbose=True)


def includeme(app: App) -> None:
    app.register_component(NAME, create_fs)

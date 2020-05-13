from __future__ import annotations
import typing as t
import pathlib

if t.TYPE_CHECKING:
    from egoist.internal.prestringutil import Module, output


def get_output(*, root: t.Union[str, pathlib.Path]) -> output[Module]:
    from egoist.registry import get_global_registry

    registry = get_global_registry()
    return registry._create_output(root=root)  # type: ignore


def includeme(app: t.Any) -> None:
    from egoist.registry import Registry

    # define method (todo: typing)
    def create_output(
        self: t.Any, *, root: t.Union[pathlib.Path, str]
    ) -> output[Module]:
        from egoist.internal.prestringutil import output, Module

        return output(root=str(root), opener=Module, verbose=True)

    Registry._create_output = create_output  # type: ignore

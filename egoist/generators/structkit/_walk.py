from __future__ import annotations
import typing as t
import typing_extensions as tx
import typing_inspect as ti
from functools import lru_cache
from metashape.declarative import MISSING
from metashape.types import Kind as NodeKind
from egoist.typing import resolve_name, guess_name
from . import runtime
from ._context import Context, Item


def walk(
    ctx: Context,
    classes: t.List[t.Type[t.Any]],
    *,
    _nonetype: t.Type[t.Any] = type(None),
    kinds: t.Optional[t.List[t.Optional[NodeKind]]] = None,
) -> t.Iterator[Item]:
    metadata_handler = ctx.metadata_handler
    w = ctx.get_metashape_walker(classes)

    kinds = kinds or ["object", None, "enum"]
    for cls in w.walk(kinds=kinds):
        origin = getattr(cls, "__origin__", None)
        if origin is not None:
            args = list(ti.get_args(cls))
            if origin == t.Union and _nonetype not in args:  # union
                yield Item(
                    name=guess_name(cls), type_=cls, fields=[], args=args, origin=origin
                )  # fixme
                for subtype in get_flatten_args(cls):
                    w.append(subtype)
                continue
            elif origin == tx.Literal:  # literal
                yield Item(
                    name=resolve_name(cls),
                    type_=cls,
                    fields=[],
                    args=args,
                    origin=origin,
                )  # fixme name
                continue
            else:
                raise RuntimeError("unexpected type {cls!r}")

        fields: t.List[runtime.Row] = []
        for name, info, _metadata in w.for_type(cls).walk(ignore_private=False):
            if name.startswith("_") and name.endswith("_"):
                continue

            filled_metadata: runtime.Metadata = runtime.metadata()
            filled_metadata.update(_metadata)  # type:ignore

            if filled_metadata.get("default") == MISSING:
                filled_metadata.pop("default")
            if info.is_optional:
                filled_metadata["required"] = False

            # handling tags
            metadata_handler(cls, name=name, info=info, metadata=filled_metadata)
            fields.append((name, info, filled_metadata))

            # append to walker, if needed
            for subtype in get_flatten_args(info.type_):
                w.append(subtype)

        yield Item(name=resolve_name(cls), type_=cls, fields=fields, args=[])


@lru_cache(maxsize=256)
def get_flatten_args(typ: t.Type[t.Any]) -> t.Tuple[t.Type[t.Any]]:
    if not hasattr(typ, "__args__"):
        if typ.__module__ != "builtins":
            return (typ,)
        return ()  # type: ignore

    r: t.Set[t.Type[t.Any]] = set()
    for subtype in typ.__args__:
        r.update(get_flatten_args(subtype))
    return tuple(sorted(r, key=id))  # type: ignore

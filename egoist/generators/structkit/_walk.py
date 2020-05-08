import typing as t
import typing_extensions as tx
import dataclasses
from metashape.declarative import MISSING
from metashape.runtime import get_walker
from . import runtime


@dataclasses.dataclass
class Item:
    type_: t.Type[t.Any]
    fields: t.List[runtime.Row]
    args: t.List[t.Type[t.Any]]
    origin: t.Optional[t.Type[t.Any]] = None

    @property
    def is_object(self) -> bool:
        return not self.args

    @property
    def is_union(self) -> bool:
        return not self.fields and bool(self.args)

    @property
    def is_enums(self) -> bool:
        return not self.fields and (
            self.origin is not None and self.origin == tx.Literal  # type: ignore
        )


def walk(
    classes: t.List[t.Type[t.Any]],
    *,
    _nonetype: t.Type[t.Any] = type(None),
    metadata_handler: t.Optional[runtime.MetadataHandlerFunction] = None,
) -> t.Iterator[Item]:
    w = get_walker(classes)
    metadata_handler = metadata_handler or runtime._default_metadata_handler

    for cls in w.walk(kinds=["object", None]):
        origin = getattr(cls, "__origin__", None)
        if origin is not None:
            args = list(t.get_args(cls))
            if origin == t.Union and _nonetype not in args:  # union
                yield Item(type_=cls, fields=[], args=args, origin=origin)
                for subtyp in args:
                    if subtyp.__module__ != "builtins":
                        w.append(subtyp)
                continue
            elif origin == t.Literal:  # literal
                yield Item(type_=cls, fields=[], args=args, origin=origin)
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

            if info.normalized.__module__ != "builtins":
                w.append(info.normalized)
            if hasattr(info.normalized, "__origin__"):  # list, dict, etc..
                for subtyp in t.get_args(info.normalized):
                    if subtyp.__module__ != "builtins":
                        w.append(subtyp)

            fields.append((name, info, filled_metadata))
        yield Item(type_=cls, fields=fields, args=[])

import typing as t
import dataclasses
from metashape.declarative import MISSING
from metashape.runtime import get_walker
from . import runtime


@dataclasses.dataclass
class Item:
    type_: t.Type[t.Any]
    fields: t.List[runtime.Row]
    args: t.List[t.Type[t.Any]]

    @property
    def is_object(self) -> bool:
        return not self.args

    @property
    def is_union(self) -> bool:
        return not self.fields and bool(self.args)


def walk(
    classes: t.List[t.Type[t.Any]], *, _nonetype: t.Type[t.Any] = type(None)
) -> t.Iterator[Item]:
    w = get_walker(classes)
    for cls in w.walk(kinds=["object", None]):
        if (
            getattr(cls, "__origin__", None) == t.Union
            and _nonetype not in cls.__args__
        ):
            yield Item(type_=cls, fields=[], args=cls.__args__)
            for subtyp in cls.__args__:
                if subtyp.__module__ != "builtins":
                    w.append(subtyp)
            continue

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
            if "json" not in filled_metadata:
                filled_metadata["tags"] = {"json": [name.rstrip("_")]}

            if info.normalized.__module__ != "builtins":
                w.append(info.normalized)
            if hasattr(info.normalized, "__origin__"):  # list, dict, etc..
                for subtyp in t.get_args(info.normalized):
                    if subtyp.__module__ != "builtins":
                        w.append(subtyp)

            fields.append((name, info, filled_metadata))
        yield Item(type_=cls, fields=fields, args=[])

from __future__ import annotations
import typing as t
import typing_extensions as tx
import typing_inspect as ti

import dataclasses
from metashape.declarative import MISSING
from metashape import typeinfo
from metashape.analyze.config import Config as MetashapeConfig  # xxx
from metashape.runtime import get_walker as _get_metashape_walker  # xxx
from metashape.types import Kind as NodeKind
from egoist.typing import resolve_name, guess_name
from egoist.langhelpers import reify
from egoist.go.types import _unwrap_pointer_type, _get_flatten_args
from egoist.go.resolver import Resolver
from egoist.internal.prestringutil import Module
from . import metadata as metadata_

if t.TYPE_CHECKING:
    from metashape.analyze.walker import Walker as MetashapeWalker  # xxx


def walk(
    w: MetashapeWalker,
    *,
    metadata_handler: metadata_.MetadataHandlerFunction,
    _nonetype: t.Type[t.Any] = type(None),
    kinds: t.Optional[t.List[t.Optional[NodeKind]]] = None,
) -> t.Iterator[Item]:
    kinds = kinds or ["object", None, "enum"]
    for cls in w.walk(kinds=kinds):
        origin = getattr(cls, "__origin__", None)
        if origin is not None:
            args = list(ti.get_args(cls))
            if origin == t.Union and _nonetype not in args:  # union
                yield Item(
                    name=guess_name(cls), type_=cls, fields=[], args=args, origin=origin
                )  # fixme
                for subtype in _get_flatten_args(cls):
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

        fields: t.List[Row] = []
        for name, info, _metadata in w.for_type(cls).walk(ignore_private=False):
            if name.startswith("_") and name.endswith("_"):
                continue

            filled_metadata: metadata_.Metadata = metadata_.metadata()
            filled_metadata.update(_metadata)  # type:ignore

            if filled_metadata.get("default") == MISSING:
                filled_metadata.pop("default")
            if info.is_optional:
                filled_metadata["required"] = False

            # handling tags
            metadata_handler(cls, name=name, info=info, metadata=filled_metadata)
            fields.append((name, info, filled_metadata))

            # append to walker, if needed
            for subtype in _get_flatten_args(info.type_):
                w.append(subtype)

        yield Item(name=resolve_name(cls), type_=cls, fields=fields, args=[])


Row = t.Tuple[str, t.Any, metadata_.Metadata]


@dataclasses.dataclass(frozen=False, eq=False)
class Context:
    m: Module
    resolver: Resolver

    _metadata_handler: t.Optional[metadata_.MetadataHandlerFunction] = None
    _unexpected_type_handler: t.Optional[
        t.Callable[[t.Type[t.Any]], typeinfo.TypeInfo]
    ] = None

    # for enums
    pseudo_item_map: t.Dict[t.Type[t.Any], Item] = dataclasses.field(
        default_factory=dict
    )

    # for GoPointer
    raw_type_map: t.Dict[typeinfo.TypeInfo, t.Type[t.Any]] = dataclasses.field(
        default_factory=dict
    )

    @reify
    def metadata_handler(self) -> metadata_.MetadataHandlerFunction:
        return self._metadata_handler or metadata_.add_jsontag_metadata_handler

    @reify
    def unexpected_type_handler(self) -> t.Callable[[t.Type[t.Any]], typeinfo.TypeInfo]:
        if self._unexpected_type_handler is not None:
            return self._unexpected_type_handler

        def _typeinfo_on_default(raw_type: t.Type[t.Any]) -> typeinfo.TypeInfo:
            typ, _ = _unwrap_pointer_type(raw_type)
            resolved = typeinfo.typeinfo(typ)
            self.raw_type_map[resolved] = raw_type
            return resolved

        return _typeinfo_on_default

    ########################################
    # actions
    ########################################

    def get_metashape_walker(self, classes: t.List[t.Type[t.Any]]) -> MetashapeWalker:
        config = MetashapeConfig(
            typeinfo_unexpected_handler=self.unexpected_type_handler
        )
        return _get_metashape_walker(classes, config=config)

    def create_pseudo_item(self, item: Item, *, discriminator_name: str) -> Item:
        pseudo_item = self.pseudo_item_map.get(item.type_)
        if pseudo_item is not None:
            return pseudo_item

        discriminator_field = (
            "$kind",
            typeinfo.typeinfo(t.NewType(discriminator_name, str)),
            metadata_.metadata(),
        )
        pseudo_fields = [
            (
                sub_type.__name__,
                typeinfo.typeinfo(t.Optional[sub_type]),
                metadata_.metadata(required=False),
            )
            for sub_type in item.args
        ]

        pseudo_item = Item(
            name=item.name,
            type_=item.type_,
            fields=[discriminator_field] + pseudo_fields,
            args=[],
        )
        self.pseudo_item_map[item.type_] = pseudo_item
        # hack: temporary
        self.pseudo_item_map[t.Optional[item.type_]] = dataclasses.replace(
            pseudo_item, name=f"*{pseudo_item.name}", type_=t.Optional[item.type_]
        )
        return pseudo_item


@dataclasses.dataclass
class Item:
    name: str
    type_: t.Type[t.Any]
    fields: t.List[Row] = dataclasses.field(repr=False)
    args: t.List[t.Type[t.Any]] = dataclasses.field(repr=False)
    origin: t.Optional[t.Type[t.Any]] = dataclasses.field(repr=False, default=None)

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

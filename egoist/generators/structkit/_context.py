from __future__ import annotations
import typing as t
import typing_extensions as tx
import dataclasses
from metashape import typeinfo
from metashape.analyze.walker import Walker as MetashapeWalker  # xxx
from metashape.analyze.config import Config as MetashapeConfig  # xxx
from metashape.runtime import get_walker
from egoist.langhelpers import reify
from egoist.go.types import _unwrap_pointer_type
from egoist.go.resolver import Resolver
from egoist.internal.prestringutil import Module
from . import runtime


@dataclasses.dataclass(frozen=False, eq=False)
class Context:
    m: Module
    resolver: Resolver

    _metadata_handler: t.Optional[runtime.MetadataHandlerFunction] = None
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
    def metadata_handler(self) -> runtime.MetadataHandlerFunction:
        return self._metadata_handler or runtime._default_metadata_handler

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
        return get_walker(classes, config=config)

    def create_pseudo_item(self, item: Item, *, name: str) -> Item:
        pseudo_item = self.pseudo_item_map.get(item.type_)
        if pseudo_item is not None:
            return pseudo_item

        discriminator_field = ("$kind", typeinfo.typeinfo(str), runtime.metadata())
        discriminator_field[-1]["_override_type"] = name

        pseudo_fields = [
            (
                sub_type.__name__,
                typeinfo.typeinfo(t.Optional[sub_type]),
                runtime.metadata(required=False),
            )
            for sub_type in item.args
        ]

        pseudo_item = Item(
            type_=item.type_, fields=[discriminator_field] + pseudo_fields, args=[],
        )
        self.pseudo_item_map[item.type_] = pseudo_item
        return pseudo_item


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

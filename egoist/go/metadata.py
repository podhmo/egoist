from __future__ import annotations
import typing as t
import typing_extensions as tx


class Metadata(tx.TypedDict, total=False):
    inline: bool
    required: bool
    comment: str
    default: t.Any
    tags: t.Dict[str, t.List[str]]


def metadata(
    *, inline: bool = False, required: bool = True, comment: str = ""
) -> Metadata:
    d: Metadata = {
        "inline": inline,
        "required": required,
        "comment": comment,
        "tags": {},
    }
    return d


class MetadataHandlerFunction(tx.Protocol):
    def __call__(
        self, cls: t.Type[t.Any], *, name: str, info: t.Any, metadata: Metadata
    ) -> None:
        ...


def add_jsontag_metadata_handler(
    cls: t.Type[t.Any], *, name: str, info: t.Any, metadata: Metadata
) -> None:
    """inject `json:"<field name>"`"""
    if "json" not in metadata:
        metadata["tags"] = {"json": [name.rstrip("_")]}

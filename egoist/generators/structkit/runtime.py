import typing as t
import typing_extensions as tx
import dataclasses
from prestring.go.codeobject import Module
from metashape.declarative import field  # noqa: F401
from egoist.runtime import get_self, printf, Env


__all__ = [
    "get_self",
    "printf",
    "Env",
    # from other library
    "field",
    # defined in this module
    "generate",
    "Metadata",
    "Row",
    "metadata",
    "Definition",
]


def generate(
    visit: t.Callable[[Env, t.List[t.Type[t.Any]]], t.ContextManager[Module]],
    *,
    classes: t.List[t.Type[t.Any]],
) -> t.ContextManager[Module]:
    c = get_self()
    env = c.stack[-1]
    return visit(env, classes)


class Metadata(tx.TypedDict, total=False):
    inline: bool
    required: bool
    comment: str
    default: t.Any
    tags: t.Dict[str, t.List[str]]


Row = t.Tuple[str, t.Any, Metadata]


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


def set_metadata_handler(handler: MetadataHandlerFunction) -> MetadataHandlerFunction:
    global _default_metadata_handler
    _default_metadata_handler = handler
    return handler


_default_metadata_handler = add_jsontag_metadata_handler


@dataclasses.dataclass(frozen=True)
class Definition:
    name: str
    code_module: t.Optional[Module]

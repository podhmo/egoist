import typing as t
import dataclasses
from prestring.go.codeobject import Module
from metashape.declarative import field  # noqa: F401
from egoist.runtime import get_current_context, printf, Env
from egoist.go.metadata import Metadata, metadata
from egoist.go.metadata import MetadataHandlerFunction, add_jsontag_metadata_handler

__all__ = [
    "get_current_context",
    "printf",
    "Env",
    # from other library
    "field",
    "metadata",
    "Metadata",
    "MetadataHandlerFunction",
    # defined in this module
    "generate",
    "Definition",
]


def generate(
    visit: t.Callable[[Env, t.List[t.Type[t.Any]], bool], t.ContextManager[Module]],
    *,
    dry_run: bool = False,
    classes: t.List[t.Type[t.Any]],
) -> t.ContextManager[Module]:
    c = get_current_context()
    env = c.stack[-1]
    return visit(env, classes, c.dry_run)


def set_metadata_handler(handler: MetadataHandlerFunction) -> MetadataHandlerFunction:
    global _default_metadata_handler
    _default_metadata_handler = handler
    return handler


_default_metadata_handler = add_jsontag_metadata_handler


@dataclasses.dataclass(frozen=True)
class Definition:
    name: str
    code_module: t.Optional[Module]

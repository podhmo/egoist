import typing as t
import typing_extensions as tx
import dataclasses
from prestring.go.codeobject import Module
from egoist.runtime import get_self, printf, Env


__all__ = [
    "get_self",
    "printf",
    "Env",
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
    _override_type: str  # hack


Row = t.Tuple[str, t.Any, Metadata]


def metadata(
    *, inline: bool = False, required: bool = True, comment: str = ""
) -> Metadata:
    d: Metadata = {"inline": inline, "required": required, "comment": comment}
    return d


@dataclasses.dataclass(frozen=True)
class Definition:
    name: str
    code_module: t.Optional[Module]

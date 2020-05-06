import typing as t
import typing_extensions as tx
import dataclasses
from prestring.go.codeobject import Module

# from egoist.runtime import ArgsAttr, _REST_ARGS_NAME
from egoist.runtime import get_self, generate, printf, Env  # noqa: F401


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


# def get_cli_options() -> ArgsAttr:
#     return get_self().stack[-1].args


# def get_cli_rest_args() -> Symbol:
#     prefix = get_self().stack[-1].prefix
#     name = _REST_ARGS_NAME
#     return Symbol(f"{prefix}.{goname(name)}")

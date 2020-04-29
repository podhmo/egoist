import typing as t
from egoist.internal.cmdutil import is_marked_subcommand
from .types import ModuleType, Command



def scan_module(
    m: ModuleType, *, is_ignored: t.Callable[[Command], bool] = is_marked_subcommand
) -> t.Dict[str, Command]:
    defs = {}
    for name, v in m.__dict__.items():
        if name.startswith("_"):
            continue
        if not callable(v):
            continue
        if getattr(v, "__module__", "") != m.__name__:
            continue
        if is_ignored(v):
            continue

        defs[v.__name__] = v
    return defs

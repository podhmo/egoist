from __future__ import annotations
import typing as t
from functools import lru_cache


@lru_cache(maxsize=256)
def _get_flatten_args(typ: t.Type[t.Any]) -> t.Tuple[t.Type[t.Any]]:
    if not hasattr(typ, "__args__"):
        if typ.__module__ != "builtins":
            return (typ,)
        return ()  # type: ignore

    r: t.Set[t.Type[t.Any]] = set()
    for subtype in typ.__args__:
        r.update(_get_flatten_args(subtype))
    return tuple(sorted(r, key=id))  # type: ignore

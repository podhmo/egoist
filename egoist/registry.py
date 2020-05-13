from __future__ import annotations
import typing as t
import dataclasses
from collections import defaultdict


@dataclasses.dataclass
class Registry:
    generators: t.Dict[str, t.List[t.Callable[..., t.Any]]] = dataclasses.field(
        default_factory=lambda: defaultdict(list)
    )
    components: t.Dict[str, t.List[object]] = dataclasses.field(
        default_factory=lambda: defaultdict(list)
    )


_global_registry = None


def set_global_registry(r: Registry) -> None:
    global _global_registry
    _global_registry = r


def get_global_registry() -> Registry:
    global _global_registry
    assert _global_registry is not None
    return _global_registry

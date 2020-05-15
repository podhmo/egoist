from __future__ import annotations
import typing as t

import dataclasses
from collections import defaultdict
from . import types
from .langhelpers import reify


@dataclasses.dataclass
class Registry:
    generators: t.Dict[str, t.List[t.Callable[..., t.Any]]] = dataclasses.field(
        default_factory=lambda: defaultdict(list)
    )
    _factories: t.Dict[str, t.List[types.ComponentFactory]] = dataclasses.field(
        default_factory=lambda: defaultdict(list)
    )
    _dryrun_factories: t.Dict[str, t.List[types.ComponentFactory]] = dataclasses.field(
        default_factory=lambda: defaultdict(list)
    )
    dry_run: t.Optional[bool] = None

    @reify
    def factories(self) -> t.Dict[str, t.List[types.ComponentFactory]]:
        if self.dry_run is None:
            raise RuntimeError("this registry is not configured")
        return self._dryrun_factories if self.dry_run else self._factories

    def configure(self, *, dry_run: bool = False) -> None:
        self.dry_run = dry_run


_global_registry = None


def set_global_registry(r: Registry) -> None:
    global _global_registry
    _global_registry = r


def get_global_registry() -> Registry:
    global _global_registry
    assert _global_registry is not None
    return _global_registry

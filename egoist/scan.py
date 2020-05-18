import typing as t
import inspect
from .types import ModuleType, TaskFunction


def scan_module(
    module: ModuleType,
    *,
    is_ignored: t.Callable[[TaskFunction], bool] = inspect.isclass,
    targets: t.Optional[t.List[str]] = None,
) -> t.Dict[str, TaskFunction]:
    targets = targets or list(module.__dict__.keys())
    defs = {}
    for name in targets:
        v = module.__dict__.get(name)
        if v is None:
            continue
        if name.startswith("_"):
            continue
        if not callable(v):
            continue
        if getattr(v, "__module__", "") != module.__name__:
            continue
        if is_ignored(v):
            continue

        defs[v.__name__] = v
    return defs

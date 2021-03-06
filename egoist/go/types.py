from __future__ import annotations
import typing as t
from egoist.langhelpers import typing_get_args
from ._types_evil import _get_flatten_args  # for mypy

if t.TYPE_CHECKING:
    from prestring.go.codeobject import Module, Symbol

T = t.TypeVar("T")

__all__ = [
    "_get_flatten_args",
    "priority",
    "GoPointer",
    "GoError",
    "GoCleanup",
    "get_gopackage",
    "set_gopackage",
    "gopackage",
    "rename",
    "_unwrap_pointer_type",
]


class priority:
    HIGH = 10
    NORMAL = 5
    LOW = 1


class GoPointer(t.Generic[T]):
    pass


class GoError:
    name = "err"
    priority = priority.HIGH

    @classmethod
    def emit(self, m: Module, err: Symbol) -> None:
        with m.if_(f"{err} != nil"):
            m.return_(err)


class GoCleanup:
    name = "cleanup"
    priority = priority.LOW

    @classmethod
    def emit(self, m: Module, cleanup: Symbol) -> None:
        m.stmt(f"defer {cleanup}()")


_DECORATE_TARGET = t.Union[t.Type[t.Any], t.Callable[..., t.Any]]


def get_gopackage(target: t.Any) -> t.Optional[str]:
    target = getattr(target, "__func__", target)
    return getattr(target, "_gopackage", None)  # type: ignore


def set_gopackage(target: t.Any, pkg: str) -> None:
    target = getattr(target, "__func__", target)
    setattr(target, "_gopackage", pkg)


def gopackage(pkg: str) -> t.Callable[[_DECORATE_TARGET], _DECORATE_TARGET]:
    name = "_gopackage"

    def do(cls_or_callable: _DECORATE_TARGET) -> _DECORATE_TARGET:
        setattr(cls_or_callable, name, pkg)
        if not isinstance(cls_or_callable, type):
            return cls_or_callable

        # ignore base classes (not use mro())
        for attr in cls_or_callable.__dict__.values():
            if hasattr(attr, "__func__"):  # staticmethod
                set_gopackage(attr, pkg)
            elif callable(attr) and isinstance(attr, type):  # class
                set_gopackage(attr, pkg)

        return cls_or_callable

    return do


def rename(name: str) -> t.Callable[..., t.Any]:
    def set_name(fn: t.Callable[..., t.Any]) -> t.Callable[..., t.Any]:
        fn.__name__ = name
        return fn

    return set_name


def _unwrap_pointer_type(
    typ: t.Type[t.Any], *, level: int = 0
) -> t.Tuple[t.Type[t.Any], int]:
    # todo: support slice, map
    # value = 0, pointer = 1, pointer of pointer = 2, ...
    if not hasattr(typ, "__origin__"):
        return typ, level

    if typ.__origin__ == GoPointer:
        return _unwrap_pointer_type(typing_get_args(typ)[0], level=level + 1)
    return typ, level

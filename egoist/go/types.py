import typing as t
from prestring.go.codeobject import Module, Symbol  # noqa F401


class priority:
    HIGH = 10
    NORMAL = 5
    LOW = 1


class GoPointer(t.Generic[t.T]):
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
    return getattr(target, "_gopackage", None)


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

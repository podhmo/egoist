import typing as t
from functools import update_wrapper

T = t.TypeVar("T")


# stolen from pyramid
class reify(t.Generic[T]):
    """cached property"""

    def __init__(self, wrapped: t.Callable[[t.Any], T]):
        self.wrapped = wrapped
        update_wrapper(self, wrapped)  # type: ignore

    def __get__(
        self, inst: t.Optional[object], objtype: t.Optional[t.Type[t.Any]] = None
    ) -> T:
        if inst is None:
            return self  # type: ignore
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val


def get_fullname_of_callable(fn: t.Optional[t.Callable[..., t.Any]]) -> str:
    if fn is None:
        return ""
    return f"{fn.__module__}:{fn.__name__}".replace("__main__:", "")


def get_position_of_callable(fn: t.Optional[t.Callable[..., t.Any]]) -> str:
    if fn is None:
        return "-"
    code = fn.__code__
    return f"{code.co_filename}L{code.co_firstlineno} -- {code.co_name}"


def get_fullname_of_type(typ: t.Type[t.Any]) -> str:
    typ = get_origin_type(typ)
    return f"{typ.__module__}.{typ.__name__}"


def get_origin_type(typ: t.Type[t.Any]) -> t.Type[t.Any]:
    if hasattr(typ, "__origin__"):
        return typ.__origin__  # type: ignore
    return typ


def get_path_from_function_name(fnname: str) -> str:
    """foo__bar__boo -> foo/bar/boo"""
    return fnname.replace("__", "/")

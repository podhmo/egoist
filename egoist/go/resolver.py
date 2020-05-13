from __future__ import annotations
import typing as t
import typing_inspect as ti
from egoist import types
from prestring.utils import UnRepr
from prestring.go import goname
from prestring.go.codeobject import Module
from egoist.typing import resolve_name_maybe
from .types import GoPointer, get_gopackage


class Resolver:
    def __init__(self, m: Module) -> None:
        self.m = m
        self.gotype_map: t.Dict[t.Type[t.Any], str] = {}
        self.parse_method_map: t.Dict[t.Type[t.Any], str] = {}
        self.default_function_map: t.Dict[
            t.Type[t.Any], t.Callable[[t.Optional[t.Any]], str]
        ] = {}

    # see mro?
    # todo: handling import
    # todo: use lru_cache?
    # todo: return Symbol?
    def resolve_gotype(
        self, typ: t.Type[t.Any], *, _none_type: t.Type[t.Any] = type(None),
    ) -> str:
        """e.g. str -> 'string' """
        if hasattr(typ, "__origin__"):
            origin = typ.__origin__
            args = ti.get_args(typ)
            if origin == dict:
                k = self.resolve_gotype(args[0])
                v = self.resolve_gotype(args[1])
                return f"map[{k}]{v}"
            elif origin == list or origin == tuple:
                v = self.resolve_gotype(args[0])
                return f"[]{v}"
            elif origin == GoPointer or (
                origin == t.Union and len(args) == 2 and _none_type in args
            ):
                v = self.resolve_gotype(args[0])
                return f"*{v}"
            else:
                name = resolve_name_maybe(typ)
                if name is not None:
                    return name
                raise RuntimeError(f"unexpected origin {origin!r}")

        gotype = self.gotype_map.get(typ)
        if gotype is not None:
            return gotype

        pkg = get_gopackage(typ)
        prefix = ""
        if pkg is not None:
            prefix = f"{self.m.import_(pkg)}."

        py_clsname = getattr(typ, "__qualname__", typ.__name__)
        if (
            "<locals>" in py_clsname
        ):  # HACK: for the type defined in closure. (e.g. t.NewType)
            py_clsname = typ.__name__

        if "." in py_clsname:
            typename = "_".join([goname(x) for x in py_clsname.split(".")])
        else:
            typename = goname(py_clsname)
        return f"{prefix}{typename}"

    def resolve_parse_method(self, typ: t.Type[t.Any]) -> str:
        """e.g. bool -> ParseBool """
        return self.parse_method_map[typ]

    def resolve_default(self, typ: t.Type[t.Any], val: t.Any) -> str:
        """e.g. str, 'value' -> "value" """
        return self.default_function_map[typ](val)

    def register(
        self,
        typ: t.Type[t.Any],
        *,
        gotype: str,
        parse_method: str,
        default_function: t.Callable[[t.Optional[t.Any]], str],
    ) -> None:
        self.gotype_map[typ] = gotype
        self.parse_method_map[typ] = parse_method
        self.default_function_map[typ] = default_function


def get_resolver(m: Module) -> Resolver:
    resolver = Resolver(m)
    setup_resolver(resolver)
    return resolver


# TODO: customizable
def setup_resolver(resolver: Resolver) -> None:
    resolver.gotype_map[t.Any] = "interface{}"  # type: ignore

    def default_str(v: t.Optional[t.Any]) -> str:
        import json  # xxx

        return UnRepr(json.dumps(v or ""))  # type: ignore

    resolver.register(
        types.str,
        gotype="string",
        parse_method="StringVar",
        default_function=default_str,
    )

    def default_bool(v: t.Optional[t.Any]) -> str:
        return "true" if v else "false"

    resolver.register(
        types.bool, gotype="bool", parse_method="BoolVar", default_function=default_bool
    )

    def default_int(v: t.Optional[t.Any]) -> str:
        return str(v or 0)

    resolver.register(
        types.int, gotype="int", parse_method="IntVar", default_function=default_int
    )

    def default_uint(v: t.Optional[t.Any]) -> str:
        return str(v or 0)

    resolver.register(
        types.uint, gotype="uint", parse_method="UintVar", default_function=default_uint
    )

    def default_int64(v: t.Optional[t.Any]) -> str:
        return str(v or 0)

    resolver.register(
        types.int64,
        gotype="int64",
        parse_method="Int64Var",
        default_function=default_int64,
    )

    def default_uint64(v: t.Optional[t.Any]) -> str:
        return str(v or 0)

    resolver.register(
        types.uint64,
        gotype="uint64",
        parse_method="Uint64Var",
        default_function=default_uint64,
    )

    def default_float(v: t.Optional[t.Any]) -> str:
        return str(v or 0.0)

    resolver.register(
        types.float,
        gotype="float",
        parse_method="FloatVar",
        default_function=default_float,
    )

    def default_duration(v: t.Optional[t.Any]) -> str:
        # xxx:
        from egoist.runtime import get_self

        m = get_self().stack[-1].m
        m.import_("time")
        return f"{str(v or 0)}*time.Second"

    resolver.register(
        types.duration,
        gotype="time.Duration",
        parse_method="DurationVar",
        default_function=default_duration,
    )

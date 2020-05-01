from __future__ import annotations
import typing as t
from egoist import types


class Resolver:
    def __init__(self) -> None:
        self.gotype_map: t.Dict[t.Type[t.Any], str] = {}
        self.parse_method_map: t.Dict[t.Type[t.Any], str] = {}
        self.default_function_map: t.Dict[
            t.Type[t.Any], t.Callable[[t.Optional[t.Any]], str]
        ] = {}

    # see mro?

    def resolve_gotype(self, typ: t.Type[t.Any]) -> str:
        return self.gotype_map[typ]

    def resolve_parse_method(self, typ: t.Type[t.Any]) -> str:
        return self.parse_method_map[typ]

    def resolve_default(self, typ: t.Type[t.Any], val: t.Any) -> str:
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


def get_resolver() -> Resolver:
    resolver = Resolver()

    def default_str(v: t.Optional[t.Any]) -> str:
        import json  # xxx

        return json.dumps(v or "")

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

    return resolver

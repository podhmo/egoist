import typing as t
import contextlib
from egoist import types
from egoist import runtime
from egoist.internal.prestringutil import goname


class Resolver:
    def __init__(self):
        self.gotype_map = {}
        self.parse_method_map = {}
        self.default_function_map = {}

    # see mro?

    def resolve_gotype(self, typ: t.Type[t.Any]) -> str:
        return self.gotype_map[typ]

    def resolve_parse_method(self, typ: t.Type[t.Any]) -> str:
        return self.parse_method_map[typ]

    def resolve_default(self, typ: t.Type[t.Any], val: t.Any) -> str:
        return self.default_function_map[typ](val)

    def register(
        self, typ: t.Type[t.Any], *, gotype: str, parse_method: str, default_function
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


@contextlib.contextmanager
def clikit(env: runtime.Env, *, resolver: Resolver = get_resolver()) -> None:
    m = env.m
    fn = env.fn
    spec = env.fnspec

    import inspect

    oneline_description = f"{fn.__name__}"
    doc = inspect.getdoc(fn)
    if doc is not None:
        new_line = "\n"
        oneline_description = f"{oneline_description} - {doc.split(new_line, 1)[0]}"

    # TODO: support normal arguments
    m.stmt("package main")
    m.stmt("// this packaage is auto generated")
    m.sep()

    m.import_("flag")
    m.import_("os")
    m.import_("log")  # xxx:

    m.stmt("// Option ...")
    with m.struct("Option"):
        for name, typ, kind in spec.keyword_arguments:
            m.stmt(f"{goname(name)} {resolver.resolve_gotype(typ)} // for `-{name}`")

    m.sep()

    with m.func("main"):
        m.stmt("opt := &Option{}")
        m.stmt(
            'cmd := flag.NewFlagSet("{}", flag.ContinueOnError)', fn.__name__,
        )
        m.stmt("cmd.Usage = func(){")
        with m.scope():
            m.stmt(f"fmt.Fprintln(cmd.Output(), `{oneline_description}`)")
            m.stmt("fmt.PrintDefaults()")
        m.append("}")

        m.sep()

        for name, typ, kind in spec.keyword_arguments:
            arg = getattr(env.args, name)

            parse_method = resolver.resolve_parse_method(typ)
            help_usage = resolver.resolve_default(str, arg.help or "-")

            default = resolver.resolve_default(typ, arg.default)

            m.stmt(
                f'cmd.{parse_method}(&opt.{goname(name)}, "{name}", {default}, {help_usage})'
            )

        m.sep()
        m.stmt("if err := cmd.Parse(os.Args[1:]); err != nil {")
        with m.scope():
            m.stmt("if err != flag.ErrHelp {")
            with m.scope():
                m.stmt("cmd.Usage()")
            m.stmt("}")
            m.stmt("os.Exit(1)")
        m.stmt("}")
        m.stmt("if err := run(opt); err != nil {")
        with m.scope():
            m.stmt('log.Fatalf("!!%+v", err)')
        m.stmt("}")

    with m.func("run", "opt *Option", return_="error"):
        yield m
        if spec.return_type == type(None):
            m.return_("nil")

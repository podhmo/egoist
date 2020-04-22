import typing as t
import pathlib
import contextlib
from prestring.output import output
from prestring.go import Module, goname
from prestring.codeobject import Symbol
from . import types
from .naming import get_path_from_function_name
from . import runtime

# todo: separate "parse, setup component, run action"
# todo: support other types
# todo: DI resolution
# todo: support use stubs


def generate_all(fns: t.Dict[str, types.Command], *, root: str) -> None:
    with output(root=root, opener=Module) as fs:
        c = runtime.get_self()

        for name, fn in fns.items():
            fpath = get_path_from_function_name(fn.__name__)

            with fs.open(str(pathlib.Path(fpath) / "main.go"), "w") as m:
                env = runtime.Env(m=m, fn=fn)
                c.stack.append(env)
                kwargs = {
                    name: Symbol(f"opt.{goname(name)}")  # xxx
                    for name, _, _ in env.fnspec.parameters
                }
                fn(**kwargs)
                c.stack.pop()


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
        from .runtime import get_self

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
def cli(env: runtime.Env, *, resolver: Resolver = get_resolver()) -> None:
    m = env.m
    fn = env.fn
    spec = env.fnspec

    # TODO: support normal arguments
    m.stmt("package main")
    m.stmt("// this packaage is auto generated")
    m.sep()

    with m.import_group() as im:
        im.import_("fmt")
        im.import_("flag")
        im.import_("os")
        im.import_("log")
        m.import_ = im.import_  # xxx

    with m.struct("Option"):
        for name, typ, kind in spec.keyword_arguments:
            m.stmt(f"{goname(name)} {resolver.resolve_gotype(typ)}")

    m.sep()

    with m.func("main"):
        m.stmt("opt := &Option{}")
        m.stmt(
            'cmd := flag.NewFlagSet("{}", flag.ContinueOnError)', fn.__name__,
        )
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


# def _extract_internal_code(fn: types.Command):
#     import inspect
#     import textwrap
#     from prestring.python.parse import parse_string, node_name

#     source = inspect.getsource(fn)
#     tree = parse_string(source)

#     func_def = tree.children[0]
#     assert node_name(func_def) == "func_def"

#     suite = func_def.children[-1]
#     assert node_name(suite) == "suite"
#     return textwrap.dedent(str(suite))

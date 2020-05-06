import typing as t
import contextlib
import inspect
from egoist import runtime
from egoist.internal.prestringutil import goname, Module
from egoist.go.resolver import get_resolver, Resolver

from . import walk as generate  # noqa: F401


@contextlib.contextmanager
def clikit(
    env: runtime.Env, *, resolver: t.Optional[Resolver] = None
) -> t.Iterator[Module]:
    m = env.m
    fn = env.fn
    spec = env.fnspec

    resolver = resolver or get_resolver(m)

    description = None
    doc = inspect.getdoc(fn)
    if doc is not None:
        description = f"{fn.__name__} - {doc}"

    # TODO: support normal arguments
    m.package("main")
    m.import_("")
    m.stmt("// this package is generated by egoist.generate.clikit")
    m.sep()

    m.stmt("// Option ...")
    with m.struct("Option"):
        for name, typ, kind in spec.keyword_arguments:
            m.stmt(f"{goname(name)} {resolver.resolve_gotype(typ)} // for `-{name}`")

        # NOTE: accessable via runtime.get_cli_rest_args()
        m.stmt(f"{goname(runtime._REST_ARGS_NAME)} []string // cmd.Args")
    m.sep()

    with m.func("main"):
        m.stmt("opt := &Option{}")

        m.import_("flag")  # import:
        m.stmt(
            'cmd := flag.NewFlagSet("{}", flag.ContinueOnError)', fn.__name__,
        )
        if description is not None:
            m.stmt("cmd.Usage = func() {")
            with m.scope():
                m.import_("fmt")  # import:
                m.stmt(f"fmt.Fprintln(cmd.Output(), `{description}`)")
                m.stmt('fmt.Fprintln(cmd.Output(), "")')
                m.stmt('fmt.Fprintln(cmd.Output(), "Usage:")')
                m.stmt("cmd.PrintDefaults()")
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

        m.import_("os")  # import:
        m.stmt("if err := cmd.Parse(os.Args[1:]); err != nil {")
        with m.scope():
            m.stmt("if err != flag.ErrHelp {")
            with m.scope():
                m.stmt("cmd.Usage()")
            m.stmt("}")
            m.stmt("os.Exit(1)")
        m.stmt("}")
        m.stmt("opt.Args = cmd.Args()")
        m.stmt("if err := run(opt); err != nil {")
        with m.scope():
            m.import_("log")  # import:
            m.stmt('log.Fatalf("!!%+v", err)')
        m.stmt("}")

    with m.func("run", "opt *Option", returns="error"):
        yield m
        if spec.return_type == type(None):  # noqa: E721
            m.return_("nil")

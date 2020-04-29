import contextlib
import inspect
from egoist import runtime
from egoist.internal.prestringutil import goname
from .go.resolver import get_resolver, Resolver


@contextlib.contextmanager
def clikit(env: runtime.Env, *, resolver: Resolver = get_resolver()) -> None:
    m = env.m
    fn = env.fn
    spec = env.fnspec

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

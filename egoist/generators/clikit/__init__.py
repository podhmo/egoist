import typing as t
import contextlib
import inspect
import logging
import pathlib
from egoist import types
from egoist.components.fs import open_fs
from egoist.go.resolver import get_resolver, Resolver
from egoist.langhelpers import get_path_from_function_name
from egoist.internal.prestringutil import Module, goname, Symbol
from egoist.components.runtimecontext import _REST_ARGS_NAME  # xxx
from . import runtime

# todo: separate "parse, setup component, run action"
# todo: support other types
# todo: separate from clikit

logger = logging.getLogger(__name__)


def walk(
    fns: t.Dict[str, types.Command],
    *,
    root: t.Union[str, pathlib.Path],
    option_prefix: str = runtime._PREFIX_DEFAULT,
) -> None:
    with open_fs(root=root) as fs:
        for name, fn in fns.items():
            logger.debug("walk %s", name)

            fpath = pathlib.Path(get_path_from_function_name(name)) / "main.go"
            with fs.open_with_tracking(fpath, "w", target=fn) as env:
                kwargs = {
                    name: Symbol(f"{option_prefix}.{goname(name)}")
                    for name, _, _ in env.fnspec.parameters
                }
                fn(**kwargs)


@contextlib.contextmanager
def clikit(
    env: runtime.Env,
    *,
    resolver: t.Optional[Resolver] = None,
    option_prefix: str = runtime._PREFIX_DEFAULT,
) -> t.Iterator[Module]:
    m = env.m
    fn = env.fn
    spec = env.fnspec

    resolver = resolver or get_resolver(m)
    opt = m.symbol(option_prefix)

    description = None
    doc = inspect.getdoc(fn)
    if doc is not None:
        description = f"{fn.__name__} - {doc}"

    # TODO: support normal arguments
    m.package("main")
    m.import_("")
    m.stmt(f"// this file is generated by {__name__}")
    m.sep()

    m.stmt("// Option ...")
    with m.struct("Option"):
        for name, typ, kind in spec.keyword_arguments:
            m.stmt(f"{goname(name)} {resolver.resolve_gotype(typ)} // for `-{name}`")

        # NOTE: accessable via runtime.get_cli_rest_args()
        m.stmt(f"{goname(_REST_ARGS_NAME)} []string // cmd.Args")
    m.sep()

    with m.func("main"):
        m.stmt(f"{opt} := &Option{{}}")

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
                f'cmd.{parse_method}(&{opt}.{goname(name)}, "{name}", {default}, {help_usage})'
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
        m.stmt(f"{opt}.Args = cmd.Args()")
        m.stmt(f"if err := run({opt}); err != nil {{")
        with m.scope():
            m.import_("log")  # import:
            m.stmt('log.Fatalf("!!%+v", err)')
        m.stmt("}")

    with m.func("run", f"{opt} *Option", returns="error"):
        yield m
        if spec.return_type == type(None):  # noqa: E721
            m.return_("nil")

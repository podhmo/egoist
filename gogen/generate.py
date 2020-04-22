import typing as t
import pathlib
import contextlib
from prestring.output import output
from prestring.go import Module, goname
from prestring.codeobject import Symbol
from .types import Command
from .naming import get_path_from_function_name
from . import runtime

# todo: separate "parse, setup component, run action"
# todo: support other types
# todo: DI resolution
# todo: support use stubs


def generate_all(fns: t.Dict[str, Command], *, root: str) -> None:
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


@contextlib.contextmanager
def cli(env: runtime.Env) -> None:
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
        for name, v, kind in spec.keyword_arguments:
            m.stmt("{} string", goname(name))

    m.sep()

    with m.func("main"):
        m.stmt("opt := &Option{}")
        m.stmt(
            'cmd := flag.NewFlagSet("{}", flag.ContinueOnError)', fn.__name__,
        )
        m.sep()

        # TODO:
        for name, v, kind in spec.keyword_arguments:
            help_usage = getattr(env.args, name).help or "-"
            m.stmt(f'cmd.StringVar(&opt.{goname(name)}, "{name}", "", "{help_usage}")')

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


# def _extract_internal_code(fn: Command):
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

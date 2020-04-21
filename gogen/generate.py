import typing as t
import pathlib
from prestring.output import output
from prestring.go import Module
from prestring.go import goname
from .types import Command
from .naming import get_path_from_function_name
from ._fnspec import fnspec

# todo: separate "parse, setup component, run action"
# todo: support other types
# todo: DI resolution
# todo: support use stubs


def generate_all(fns: t.Dict[str, Command], *, root: str) -> None:
    with output(root=root, opener=Module) as fs:
        for name, fn in fns.items():
            fpath = get_path_from_function_name(fn.__name__)

            with fs.open(str(pathlib.Path(fpath) / "main.go"), "w") as m:
                spec = fnspec(fn)

                # TODO: support normal arguments
                m.stmt("package main")
                m.stmt("// this packaage is auto generated")
                m.sep()

                with m.import_group() as im:
                    im.import_("fmt")
                    im.import_("flag")
                    im.import_("os")
                    im.import_("log")

                with m.struct("Option"):
                    for name, v, kind in spec.keyword_arguments:
                        m.stmt("{} string", goname(name))

                m.sep()

                with m.func("main"):
                    m.stmt("opt := &Option{}")
                    m.stmt(
                        'cmd := flag.NewFlagSet("{}", flag.ContinueOnError)',
                        fn.__name__,
                    )
                    m.sep()

                    # TODO:
                    for name, v, kind in spec.keyword_arguments:
                        m.stmt(
                            'cmd.StringVar(&opt.{}, "{}", "", "-")', goname(name), name
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
                    m.stmt("""fmt.Printf("%#+v\\n", *opt)""")
                    m.return_("nil")

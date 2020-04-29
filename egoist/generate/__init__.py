import typing as t
import pathlib
from egoist import types
from egoist import runtime
from egoist.naming import get_path_from_function_name
from egoist.internal.prestringutil import output, Module, goname, Symbol

# todo: separate "parse, setup component, run action"
# todo: support other types
# todo: DI resolution
# todo: support use stubs


def walk(fns: t.Dict[str, types.Command], *, root: str) -> None:
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

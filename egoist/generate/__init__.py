import typing as t
import pathlib
from egoist import types
from egoist import runtime
from egoist.naming import get_path_from_function_name
from egoist.internal.prestringutil import output, Module, goname, Symbol

# todo: separate "parse, setup component, run action"
# todo: support other types
# todo: separate from clikit


def walk(fns: t.Dict[str, types.Command], *, root: str) -> None:
    with output(root=root, opener=Module) as fs:
        c = runtime.get_self()

        for name, fn in fns.items():
            fpath = get_path_from_function_name(fn.__name__)

            with fs.open(str(pathlib.Path(fpath) / "main.go"), "w") as m:
                env = runtime.Env(m=m, fn=fn, prefix="opt")  # xxx:
                c.stack.append(env)
                kwargs = {
                    name: Symbol(f"{env.prefix}.{goname(name)}")
                    for name, _, _ in env.fnspec.parameters
                }
                fn(**kwargs)
                c.stack.pop()

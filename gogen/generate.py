import typing as t
import pathlib
from prestring.output import output
from .scan import Command
from .naming import get_path_from_function_name


def generate_all(fns: t.Dict[str, Command], *, root: str) -> None:
    with output(root=root) as fs:
        for name, fn in fns.items():
            fpath = get_path_from_function_name(fn.__name__)

            with fs.open(str(pathlib.Path(fpath) / "main.go"), "w") as wf:
                wf.write("package main")

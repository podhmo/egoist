import typing as t
from prestring.output import output
from .scan import scan_module, Command
from .naming import get_path_from_function_name


def generate_all(fns: t.Dict[str, Command], *, root: str):
    with output(root=root) as fs:
        for name, fn in fns.items():
            fpath = get_path_from_function_name(fn.__name__)
            with fs.open(fpath, "w") as wf:
                wf.write("hai")


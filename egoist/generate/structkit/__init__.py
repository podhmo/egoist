import typing as t
import logging
import pathlib
import contextlib
from egoist import types
from egoist.internal.prestringutil import output, Module, goname, Symbol
from egoist.go.resolver import Resolver, get_resolver
from egoist.langhelpers import get_path_from_function_name
from . import runtime

logger = logging.getLogger(__name__)


def walk(fns: t.Dict[str, types.Command], *, root: t.Union[str, pathlib.Path]) -> None:
    with output(root=str(root), opener=Module) as fs:
        c = runtime.get_self()

        for name, fn in fns.items():
            logger.info("walk %s", name)

            fpath = get_path_from_function_name(name)

            with fs.open(str(pathlib.Path(fpath)) + ".go", "w") as m:  # type: Module
                env = runtime.Env(m=m, fn=fn)  # xxx:
                c.stack.append(env)
                fn()
                c.stack.pop()


@contextlib.contextmanager
def structkit(
    env: runtime.Env,
    classes: t.List[t.Type[t.Any]],
    *,
    resolver: t.Optional[Resolver] = None,
) -> t.Iterator[Module]:
    from . import _walk
    from . import _emit

    m = env.m
    resolver = resolver or get_resolver(m)
    yield m

    for item in _walk.walk(classes):
        if item.is_union:
            _emit.emit_union(m, item, resolver=resolver)
            m.sep()
        else:
            _emit.emit_struct(m, item, resolver=resolver)
            m.sep()
            if item.fields:
                _emit.emit_unmarshalJSON(m, item, resolver=resolver)
            m.sep()
    return m

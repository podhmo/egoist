import typing as t
import logging
import pathlib
import contextlib
from egoist import types
from egoist.components.fs import open_fs
from egoist.internal.prestringutil import Module
from egoist.go.resolver import Resolver, get_resolver
from egoist.langhelpers import get_path_from_function_name
from . import runtime

logger = logging.getLogger(__name__)

# TODO: suffix


def walk(fns: t.Dict[str, types.Command], *, root: t.Union[str, pathlib.Path]) -> None:
    with open_fs(root=root) as fs:
        for name, fn in fns.items():
            logger.debug("walk %s", name)
            fpath = f"{get_path_from_function_name(name)}.go"
            with fs.open_with_tracking(fpath, "w", target=fn):
                fn()


@contextlib.contextmanager
def filekit(
    env: runtime.Env,
    classes: t.List[t.Type[t.Any]],
    dry_run: bool,
    *,
    resolver: t.Optional[Resolver] = None,
) -> t.Iterator[Module]:
    if dry_run:
        logger.debug("dry run, %s skipped", __name__)
        yield env.m
        return

    m = env.m
    resolver = resolver or get_resolver(m)
    yield m

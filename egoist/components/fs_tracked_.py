from __future__ import annotations
import typing as t

import pathlib
import contextlib

from prestring.minifs import MiniFS
from egoist.internal.prestringutil import output, Module
from egoist.langhelpers import reify
from egoist import runtime
from egoist import types
from .tracker import get_tracker

Content = t.Union[str, Module, t.IO[str]]
T = t.TypeVar("T", bound=Content)


class _TrackedOutput(output[Content]):
    @reify
    def fs(self) -> _TrackedFS:  # type: ignore
        assert self.opener is not None
        return _TrackedFS(opener=self.opener, sep=self.sep)

    def __enter__(self) -> _TrackedFS:
        return self.fs


class _TrackedFS(MiniFS[Content]):
    @contextlib.contextmanager
    def open_file_with_tracking(
        self,
        fpath: t.Union[str, pathlib.Path],
        mode: str,
        *,
        target: types.Command,
        opener: t.Optional[t.Callable[[], T]] = None,
        depends_on: t.Optional[t.Collection[str]] = None
    ) -> t.Iterator[runtime.Env]:
        fpath = str(fpath)
        get_tracker().track(fpath, task=target, depends_on=depends_on)

        with self.open(fpath, mode, opener=opener) as m:
            c = runtime.get_current_context()
            env = runtime.Env(_content=m, fn=target, fpath=fpath, fs=self)

            c.stack.append(env)
            yield env
        c.stack.pop()

    @contextlib.contextmanager
    def open_dir_with_tracking(
        self,
        fpath: t.Union[str, pathlib.Path],
        *,
        target: types.Command,
        depends_on: t.Optional[t.Collection[str]] = None
    ) -> t.Iterator[runtime.Env]:
        fpath = str(fpath)

        c = runtime.get_current_context()
        env = runtime.Env(_content="", fn=target, fpath=fpath, fs=self)

        c.stack.append(env)
        yield env
        c.stack.pop()

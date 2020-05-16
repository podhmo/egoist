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


class _TrackedOutput(output[Module]):
    @reify
    def fs(self) -> _TrackedFS:  # type: ignore
        assert self.opener is not None
        return _TrackedFS(opener=self.opener, sep=self.sep)

    def __enter__(self) -> _TrackedFS:
        return self.fs


class _TrackedFS(MiniFS[Module]):
    @contextlib.contextmanager
    def open_with_tracking(
        self,
        name: t.Union[str, pathlib.Path],
        mode: str,
        *,
        target: types.Command,
        opener: t.Optional[t.Callable[[], Module]] = None,
        depends_on: t.Optional[t.Collection[str]] = None
    ) -> t.Iterator[runtime.Env]:
        get_tracker().track(name, depends_on=depends_on)

        with self.open(name, mode, opener=opener) as m:
            c = runtime.get_current_context()
            env = runtime.Env(m=m, fn=target)
            c.stack.append(env)
            yield env
        c.stack.pop()

from __future__ import annotations
import typing as t
import dataclasses
from collections import defaultdict
import logging
from miniconfig import Configurator as _Configurator
from miniconfig import Context as _Context
from .langhelpers import reify

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Registry:
    generate_settings: t.Dict[str, t.List[str]] = dataclasses.field(
        default_factory=lambda: defaultdict(list)
    )


class Context(_Context):
    @reify
    def registry(self) -> Registry:
        return Registry()


class App(_Configurator):
    context_factory = Context

    @property
    def registry(self) -> Registry:
        return self.context.registry

    def commit(self) -> App:
        logger.info("commit")
        super().commit()

    def describe(self):
        self.commit()

        import json
        import inspect

        defs = {}
        for kit, fns in self.registry.generate_settings.items():
            for fn in fns:
                name = f"{fn.__module__}.{fn.__name__}".replace("__main__.", "")
                summary = (inspect.getdoc(fn) or "").strip().split("\n", 1)[0]
                defs[name] = {"doc": summary, "generator": kit}
        d = {"definitions": defs}
        print(json.dumps(d, indent=2, ensure_ascii=False))

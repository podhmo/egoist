from __future__ import annotations
import typing as t
from egoist.go import di
from egoist.go.types import GoError, GoCleanup
from egoist.internal.prestringutil import Module


class Config:
    pass


class X:
    pass


class Y:
    pass


class Z:
    pass


class providers:
    @staticmethod
    def NewConfig(filename: str) -> t.Tuple[Config, GoError]:
        pass

    @staticmethod
    def NewX(config: Config) -> t.Tuple[X, GoCleanup]:
        pass

    @staticmethod
    def NewY(config: Config) -> t.Tuple[Y, GoCleanup, GoError]:
        pass

    @staticmethod
    def NewZ(x: X, y: Y) -> t.Tuple[Z, GoError]:
        pass


m = Module()
with m.func("run"):
    config = m.let("config", '"config.json"')
    m.sep()

    b = di.Builder()

    b.add_provider(providers.NewConfig)
    b.add_provider(providers.NewX)
    b.add_provider(providers.NewY)
    b.add_provider(providers.NewZ)

    injector = b.build(variables={"filename": config})
    z = injector.inject(m)

    m.return_(z.Run())
print(m)

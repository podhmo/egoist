from __future__ import annotations
from egoist.internal.graph import Builder
from egoist.go import di
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
    def NewConfig(filename: str) -> Config:
        pass

    @staticmethod
    def NewX(config: Config) -> X:
        pass

    @staticmethod
    def NewY(config: Config) -> Y:
        pass

    @staticmethod
    def NewZ(x: X, y: Y) -> Z:
        pass


m = Module()
with m.func("run"):
    config = m.let("config", '"config.json"')
    m.sep()

    b = Builder()

    b.add_node(**di.parse(providers.NewConfig))
    b.add_node(**di.parse(providers.NewX))
    b.add_node(**di.parse(providers.NewY))
    b.add_node(**di.parse(providers.NewZ))

    g = b.build()
    variables = di.primitives(g, {"filename": config})
    z = di.inject(m, g, variables=variables)

    m.return_(z.Run())

print(m)

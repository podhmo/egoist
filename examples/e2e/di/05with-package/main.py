from __future__ import annotations
import typing as t
from egoist.internal.graph import Builder
from egoist.go import di
from egoist.go.types import GoError, GoTeardown
from egoist.internal.prestringutil import go_file
from egoist.internal.cmdutil import as_command


class Config:
    gopackage = "m/conf"


class X:
    gopackage = "m/internal"


class Y:
    gopackage = "m/internal"


class Z:
    gopackage = "m/internal"


class providers:
    @staticmethod
    def NewConfig(filename: str) -> t.Tuple[Config, GoError]:
        pass

    @staticmethod
    def NewX(config: Config) -> t.Tuple[X, GoTeardown]:
        pass

    @staticmethod
    def NewY(config: Config) -> t.Tuple[Y, GoTeardown, GoError]:
        pass

    @staticmethod
    def NewZ(x: X, y: Y) -> t.Tuple[Z, GoError]:
        pass


@as_command  # type: ignore
def run() -> None:
    m = go_file("main")
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

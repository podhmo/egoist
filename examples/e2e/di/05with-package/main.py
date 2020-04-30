from __future__ import annotations
import typing as t
from egoist.internal.graph import Builder
from egoist.go import di
from egoist.go.types import GoError, GoTeardown, gopackage
from egoist.internal.prestringutil import gofile
from egoist.internal.cmdutil import as_command


@gopackage("m/conf")
class Config:
    pass


@gopackage("m/conf")
def NewConfig(filename: str) -> t.Tuple[Config, GoError]:
    pass


@gopackage("m/internal")
class internal:
    class X:
        pass

    class Y:
        pass

    class Z:
        pass

    @staticmethod
    def NewX(config: Config) -> t.Tuple[internal.X, GoTeardown]:
        pass

    @staticmethod
    def NewY(config: Config) -> t.Tuple[internal.Y, GoTeardown, GoError]:
        pass

    @staticmethod
    def NewZ(x: internal.X, y: internal.Y) -> t.Tuple[internal.Z, GoError]:
        pass


@as_command  # type: ignore
def run() -> None:
    m = gofile("main")
    with m.func("run"):
        config = m.let("config", '"config.json"')
        m.sep()

        b = Builder()

        b.add_node(**di.parse(NewConfig))
        b.add_node(**di.parse(internal.NewX))
        b.add_node(**di.parse(internal.NewY))
        b.add_node(**di.parse(internal.NewZ))

        g = b.build()
        variables = di.primitives(g, {"filename": config})
        z = di.inject(m, g, variables=variables)

        m.return_(z.Run())
    print(m)

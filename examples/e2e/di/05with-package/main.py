from __future__ import annotations
import typing as t
from egoist.go import di
from egoist.go.types import GoError, GoCleanup, gopackage
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
    def NewX(config: Config) -> t.Tuple[internal.X, GoCleanup]:
        pass

    @staticmethod
    def NewY(config: Config) -> t.Tuple[internal.Y, GoCleanup, GoError]:
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

        b = di.Builder()

        b.add_provider(NewConfig)
        b.add_provider(internal.NewX)
        b.add_provider(internal.NewY)
        b.add_provider(internal.NewZ)

        injector = b.build(variables={"filename": config})
        z = injector.inject(m)

        m.return_(z.Run())
    print(m)

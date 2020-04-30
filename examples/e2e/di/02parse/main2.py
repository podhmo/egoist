from __future__ import annotations
from egoist.go import di
from egoist.internal.prestringutil import Module
from egoist.internal.cmdutil import as_command


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


@as_command  # type: ignore
def run() -> None:
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

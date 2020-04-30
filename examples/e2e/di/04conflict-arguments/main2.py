from __future__ import annotations
from egoist.go import di
from egoist.internal.prestringutil import Module
from egoist.internal.cmdutil import as_command


class X:
    pass


class Y:
    pass


class Z:
    pass


class providers:
    @staticmethod
    def NewX(x_filename: str) -> X:
        pass

    @staticmethod
    def NewY(y_filename: str) -> Y:
        pass

    @staticmethod
    def NewZ(x: X, y: Y) -> Z:
        pass


@as_command  # type: ignore
def run() -> None:
    m = Module()

    m.stmt("// But, in python, using the argument of different name")
    m.sep()

    with m.func("run2"):
        config = m.let("config", '"config.json"')
        config2 = m.let("config2", '"config2.json"')

        m.sep()

        b = di.Builder()

        b.add_provider(providers.NewX)
        b.add_provider(providers.NewY)
        b.add_provider(providers.NewZ)

        injector = b.build(variables={"x_filename": config, "y_filename": config2})
        z = injector.inject(m)

        m.return_(z.Run())
    print(m)

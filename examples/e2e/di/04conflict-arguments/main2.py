from __future__ import annotations
from egoist.internal.graph import Builder
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

        b = Builder()

        b.add_node(**di.parse(providers.NewX))
        b.add_node(**di.parse(providers.NewY))
        b.add_node(**di.parse(providers.NewZ))

        g = b.build()
        variables = di.primitives(g, {"x_filename": config, "y_filename": config2})
        z = di.inject(m, g, variables=variables)

        m.return_(z.Run())
    print(m)

from egoist.internal.graph import Builder, primitive
from egoist.go import di
from egoist.internal.prestringutil import Module
from egoist.internal.cmdutil import as_command


@as_command  # type: ignore
def run() -> None:
    m = Module()
    with m.func("run"):
        config = m.let("config", '"config.json"')
        m.sep()

        b = Builder()

        b.add_node("Config", depends=[primitive("filename")])
        b.add_node("X", depends=["Config"])
        b.add_node("Y", depends=["Config"])
        b.add_node("Z", depends=["X", "Y"])

        g = b.build()
        variables = di.primitives(g, {"filename": config})
        z = di.inject(m, g, variables=variables)

        m.return_(z.Run())
    print(m)

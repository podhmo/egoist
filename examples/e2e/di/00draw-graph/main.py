from egoist.internal.graph import Builder, primitive
from egoist.internal.graph import draw
from egoist.internal.cmdutil import as_command


@as_command  # type: ignore
def run() -> None:
    b = Builder()

    b.add_node("Config", depends=[primitive("filename")])
    b.add_node("X", depends=["Config"])
    b.add_node("Y", depends=["Config"])
    b.add_node("Z", depends=["X", "Y"])

    g = b.build()
    print(draw.visualize(g))

from egoist.internal.graph import Builder, primitive
from egoist.internal.graph import draw


b = Builder()

b.add_node("Config", depends=[primitive("filename")])
b.add_node("X", depends=["Config"])
b.add_node("Y", depends=["Config"])
b.add_node("Z", depends=["X", "Y"])

g = b.build()
print(draw.visualize(g))

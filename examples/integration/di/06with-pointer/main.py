from __future__ import annotations
from egoist.go import di
from egoist.go.types import GoPointer, gopackage
from egoist.internal.prestringutil import gofile


"""
x := NewX() // X{}
y := NewY(&x)
z := NewZ(x, *y)
"""


@gopackage("m/internal")
class internal:
    class X:
        pass

    class Y:
        pass

    class Z:
        pass

    @staticmethod
    def NewX() -> internal.X:
        pass

    @staticmethod
    def NewY(x: GoPointer[internal.X]) -> GoPointer[internal.Y]:
        pass

    @staticmethod
    def NewZ(x: internal.X, y: internal.Y) -> GoPointer[internal.Z]:
        pass


m = gofile("main")
with m.func("run", returns="error"):
    b = di.Builder()

    b.add_provider(internal.NewX)
    b.add_provider(internal.NewY)
    b.add_provider(internal.NewZ)

    injector = b.build()
    z = injector.inject(m)

    m.return_(z.Run())
print(m)

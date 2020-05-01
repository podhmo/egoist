from __future__ import annotations
import typing as t
from egoist.go import di
from egoist.go.types import GoError, GoCleanup
from egoist.internal.prestringutil import Module


"""
X -> Y0 -> Z0
  -> Y1 -> Z1
"""


class X:
    pass


class Y0:
    pass


class Z0:
    pass


class Y1:
    pass


class Z1:
    pass


def NewX() -> X:
    pass


def NewY0(x: X) -> Y0:
    pass


def NewZ0(y: Y0) -> Z0:
    pass


def NewY1(x: X) -> Y1:
    pass


def NewZ1(y: Y1) -> Z1:
    pass


m = Module()
b = di.Builder()

b.add_provider(NewX)
b.add_provider(NewY0)
b.add_provider(NewZ0)
b.add_provider(NewY1)
b.add_provider(NewZ1)

injector = b.build()

z0 = injector.inject(m, provider=NewZ0)
z1 = injector.inject(m, provider=NewZ1)
z1 = injector.inject(m, provider=NewZ1)

m.stmt("({}, {})", z0, z1)

print(m)

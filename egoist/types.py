import typing as t
import types

ModuleType = types.ModuleType
Command = t.Callable[..., t.Any]


########################################
# primitives
########################################

# bool
bool = bool
# int
int = int
# int64
int64 = t.NewType("int64", int)
# uint
uint = t.NewType("uint", int)
# uint64
uint64 = t.NewType("uint64", int)
# string
str = string = str
# float
float = float
# float64
float64 = float

# dtime.Duration
duration = t.NewType("duration", int)


########################################
# go builtin type
########################################
from prestring.go.codeobject import Module, Symbol  # noqa F401


class GoError:
    name = "err"
    priority = 10

    @classmethod
    def emit(self, m: Module, err: Symbol) -> None:
        with m.if_(f"{err} != nil"):
            m.return_(err)


class GoTeardown:
    name = "teardown"
    priority = 1

    @classmethod
    def emit(self, m: Module, teardown: Symbol) -> None:
        m.stmt(f"defer {teardown}()")

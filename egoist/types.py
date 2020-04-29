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

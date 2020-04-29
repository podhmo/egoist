from __future__ import annotations
import typing as t
from prestring.go.codeobject import Module, Symbol


class Message:
    gopackage = "m/internal"


class Greeter:
    gopackage = "m/internal"


class Event:
    gopackage = "m/internal"


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


def NewMessage() -> Message:
    pass


def NewGreeter(message: Message) -> Greeter:
    pass


def NewEvent(g: Greeter) -> t.Tuple[Event, GoError]:
    pass

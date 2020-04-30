from __future__ import annotations
import typing as t
from egoist.go.types import GoError, gopackage


class Message:
    pass


class Greeter:
    pass


class Event:
    pass


@gopackage("m/internal")
def NewMessage() -> Message:
    pass


@gopackage("m/internal")
def NewGreeter(message: Message, grumby: bool) -> Greeter:
    pass


@gopackage("m/internal")
def NewEvent(g: Greeter) -> t.Tuple[Event, GoError]:
    pass

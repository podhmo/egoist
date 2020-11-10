from egoist.go.types import gopackage


@gopackage("time")
class Time:
    pass


class Todo:
    Content: str
    CreatedAt: Time

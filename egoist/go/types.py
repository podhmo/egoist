from prestring.go.codeobject import Module, Symbol  # noqa F401


class priority:
    HIGH = 10
    NORMAL = 5
    LOW = 1


class GoError:
    name = "err"
    priority = priority.HIGH

    @classmethod
    def emit(self, m: Module, err: Symbol) -> None:
        with m.if_(f"{err} != nil"):
            m.return_(err)


class GoTeardown:
    name = "teardown"
    priority = priority.LOW

    @classmethod
    def emit(self, m: Module, teardown: Symbol) -> None:
        m.stmt(f"defer {teardown}()")

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

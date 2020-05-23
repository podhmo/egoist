from __future__ import annotations
import typing as t


AnyFunction = t.Callable[..., t.Any]
if t.TYPE_CHECKING:
    from egoist.app import App


class SubApp:
    def __init__(self):
        self.registered = []
        self.requires = set()

    def define_cli(self, kit: str) -> AnyFunction:
        self.requires.add("egoist.directives.define_cli")

        def _register(task: AnyFunction) -> AnyFunction:
            self.registered.append(("define_cli", (kit,), {}, task))

        return _register

    def includeme(self, app: App):
        seen = app.imported
        for path in self.requires:
            if path in seen:
                continue
            app.include(path)

        for name, args, kwargs, task in self.registered:
            get_directive = getattr(app, name)
            directive = get_directive(*args, *kwargs)
            directive(task)


def create_subapp(*, _depth: int = 1) -> SubApp:
    import sys

    subapp = SubApp()

    # black magic: register includeme automatically
    f = sys._getframe(_depth)
    if "includeme" not in f.f_globals:
        f.f_globals["includeme"] = subapp.includeme
    return subapp

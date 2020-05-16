from __future__ import annotations
import typing as t
import typing_extensions as tx
import pathlib
from egoist.app import App
from egoist import runtime

NAME = __name__


class Dependency(tx.TypedDict):
    name: str
    depends: t.Set[str]


class Tracker:
    def __init__(self) -> None:
        self.deps_map: t.Dict[str, Dependency] = {}

    def track(
        self,
        name_or_path: t.Union[str, pathlib.Path],
        *,
        depends_on: t.Optional[t.Collection[str]]
    ) -> None:
        name = str(name_or_path)
        dependency = self.deps_map.get(name)
        if dependency is None:
            dependency = self.deps_map[name] = {"name": name, "depends": set()}
        if depends_on:
            dependency["depends"].update(depends_on)

    def get_dependencies(self, relative: bool = False) -> t.Dict[str, t.List[str]]:
        if not relative:
            return {dep["name"]: list(dep["depends"]) for dep in self.deps_map.values()}

        cwd_path = pathlib.Path().absolute()
        root_path = pathlib.Path(
            runtime.get_current_context().registry.settings["rootdir"]
        ).absolute()
        return {
            str((root_path / name).relative_to(cwd_path)): [
                str((root_path / x).relative_to(cwd_path)) for x in dep["depends"]
            ]
            for name, dep in self.deps_map.items()
        }


def get_tracker() -> Tracker:
    return t.cast(Tracker, runtime.get_component(NAME))


def includeme(app: App) -> None:
    app.register_factory(NAME, Tracker)
    app.register_dryurn_factory(NAME, Tracker)

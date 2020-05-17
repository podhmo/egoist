# copied from monogusa/web/codegen/_fnspec.py
from __future__ import annotations
import typing as t
import typing_extensions as tx

import sys
import pathlib
import inspect
import dataclasses
from functools import update_wrapper
from egoist.langhelpers import reify

# note: internal package, need to merge with metashape's one?


@dataclasses.dataclass
class Fnspec:
    body: t.Callable[..., t.Any]
    argspec: inspect.FullArgSpec = dataclasses.field(hash=False)
    _module: t.Optional[str] = dataclasses.field(default=None, hash=False, repr=False)
    _aliases: t.Dict[str, str] = dataclasses.field(
        hash=False, repr=False, default_factory=lambda: {"typing": "t"},  # xxx:
    )

    @property
    def name(self) -> str:
        return self.body.__name__

    @property
    def module(self) -> str:
        m = self._module or self.body.__module__
        return self._aliases.get(m, m)

    @property
    def fullname(self) -> str:
        return f"{self.module}.{self.name}"

    @property
    def shortname(self) -> str:
        return self.name.split("__", 1)[-1]

    @property
    def doc(self) -> t.Optional[str]:
        return inspect.getdoc(self.body)

    @property
    def is_coroutinefunction(self) -> bool:
        return inspect.iscoroutinefunction(self.body)

    def kind_of(self, name: str) -> Kind:
        return self._classified[name]

    def default_of(self, name: str) -> t.Any:
        return self._defaults.get(name)

    @reify
    def parameters(self) -> t.List[t.Tuple[str, t.Type[t.Any], Kind]]:
        """arguments + keyword_arguments"""
        return [
            (name, v, self.kind_of(name))
            for name, v in self.argspec.annotations.items()
            if name != "return"
        ]

    @reify
    def return_type(self) -> t.Type[t.Any]:
        val = self.argspec.annotations["return"]  # type: t.Type[t.Any]
        return val

    @reify
    def arguments(self) -> t.List[t.Tuple[str, t.Type[t.Any], Kind]]:
        return [
            (name, v, kind)
            for name, v, kind in self.parameters
            if kind.startswith("arg")
        ]

    @reify
    def keyword_arguments(self) -> t.List[t.Tuple[str, t.Type[t.Any], Kind]]:
        return [
            (name, v, kind)
            for name, v, kind in self.parameters
            if kind.startswith("kw")
        ]

    @reify
    def _classified(self) -> t.Dict[str, Kind]:
        return _classify_args(self.argspec)

    @reify
    def _defaults(self) -> t.Dict[str, t.Any]:
        defaults = self.argspec.kwonlydefaults or {}
        if self.argspec.defaults:
            for val, name in zip(
                reversed(self.argspec.defaults), reversed(self.argspec.args)
            ):
                defaults[name] = val
        return defaults

    @reify
    def here(self) -> pathlib.Path:
        return pathlib.Path(sys.modules[self.body.__module__].__file__).absolute()


def fnspec(fn: t.Callable[..., t.Any]) -> Fnspec:
    argspec = inspect.getfullargspec(fn)
    annotations = t.get_type_hints(fn)
    assert len(argspec.annotations) == len(annotations), (
        len(argspec.annotations),
        len(annotations),
    )
    argspec.annotations.update(annotations)
    spec = Fnspec(fn, argspec=argspec)
    update_wrapper(spec, fn)  # type: ignore
    return spec


Kind = tx.Literal["args", "args_defaults", "kw", "kw_defaults", "var_args", "var_kw"]


def _classify_args(spec: inspect.FullArgSpec) -> t.Dict[str, Kind]:
    classified: t.Dict[str, Kind] = {}
    args_limit = len(spec.args or []) - len(spec.defaults or [])
    for i in range(args_limit):
        classified[spec.args[i]] = "args"
    for i in range(1, len(spec.defaults or []) + 1):
        classified[spec.args[-i]] = "args_defaults"
    for k in spec.kwonlyargs:
        classified[k] = "kw"
    for k in spec.kwonlydefaults or []:
        classified[k] = "kw_defaults"
    if spec.varkw:
        classified[spec.varkw] = "var_kw"
    if spec.varargs:
        classified[spec.varargs] = "var_args"
    return classified

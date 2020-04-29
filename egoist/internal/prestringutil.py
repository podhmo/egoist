import typing as t
from prestring.go import Module as _Module
from prestring.go import goname, ImportGroup
from prestring.output import output
from prestring.codeobject import Symbol
from prestring.utils import reify

__all__ = ["goname", "Symbol", "output", "Module"]


# todo: fix in prestring.go
class Module(_Module):
    @reify
    def _toplevel_import_area(self) -> ImportGroup:
        with self.import_group() as ig:
            pass
        return ig

    def import_(self, path: str, as_: t.Optional[str] = None) -> Symbol:
        self._toplevel_import_area.import_(path, as_=as_)
        name = as_ or path.rsplit("/", 1)[-1]  # xxx (error in go-sqlite)
        return Symbol(name)

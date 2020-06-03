import typing as t
import typing_extensions as tx
from prestring.utils import LazyArgumentsAndKeywords, UnRepr


class Stringer(tx.Protocol):
    def __str__(self) -> str:
        ...


def as_value(
    val: t.Any,
) -> t.Union[t.Dict[str, t.Any], t.List[t.Any], t.Tuple[t.Any, ...], str, UnRepr]:
    if isinstance(val, dict):
        return {k: as_value(v) for k, v in val.items()}
    elif isinstance(val, (tuple, list)):
        return val.__class__([as_value(v) for v in val])
    elif hasattr(val, "emit"):
        return UnRepr(val)
    elif callable(val) and hasattr(val, "__name__"):
        return val.__name__  # type: ignore # todo: fullname
    else:
        return repr(val)


class _NoEffectContextManager:
    def __enter__(self) -> "Attr":
        return Attr("__enter__", co=self)

    def __exit__(
        self,
        exc: t.Optional[t.Type[BaseException]],
        value: t.Optional[BaseException],
        tb: t.Any,
    ) -> None:
        pass


class Object(_NoEffectContextManager):
    emit = None  # for as_value

    def __init__(self, name: str) -> None:
        self.name = name
        self._use_count = 0

    def __str__(self) -> str:
        return self.name

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> "Call":
        return Call(name=self.name, co=self, args=args, kwargs=kwargs)

    def __getitem__(self, name: str) -> "Getitem":
        return Getitem(name, co=self)

    def __getattr__(self, name: str) -> "Attr":
        if self._use_count > 1:
            raise RuntimeError("assign to a variable")
        self._use_count += 1
        return Attr(name, co=self)


class Symbol(_NoEffectContextManager):
    emit = None  # for as_value

    def __init__(self, name: str, as_: t.Optional[str] = None):
        self.name = name
        self.as_ = as_

    def __str__(self) -> str:
        return self.as_ or self.name

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> "Call":
        return Call(self.as_ or self.name, co=self, args=args, kwargs=kwargs)

    def __getitem__(self, name: str) -> "Getitem":
        return Getitem(name, co=self)

    def __getattr__(self, name: str) -> "Attr":
        # if name == "emit":
        #     raise AttributeError(name)
        return Attr(name, co=self)


class Attr(_NoEffectContextManager):
    emit = None  # for as_value

    __slots__ = (
        "name",
        "_co",
    )

    def __init__(self, name: str, co: Stringer) -> None:
        self.name = name
        self._co = co

    def __str__(self) -> str:
        return f"{self._co}.{self.name}"

    def __call__(self, *args: t.Any, **kwargs: t.Any) -> "Call":
        return Call(self.name, co=self, args=args, kwargs=kwargs)

    def __getitem__(self, name: str) -> "Getitem":
        return Getitem(name, co=self)

    def __getattr__(self, name: str) -> "Attr":
        # if name == "emit":
        #     raise AttributeError(name)
        return Attr(name, co=self)


class Getitem(Attr):
    def __str__(self) -> str:
        return f'{self._co}["{self.name}"]'


class Call(_NoEffectContextManager):
    emit = None  # for as_value

    def __init__(
        self,
        name: str,
        *,
        co: Stringer,
        args: t.Tuple[t.Any, ...],
        kwargs: t.Dict[str, t.Any],
    ) -> None:
        self._name = name

        self._co = co
        self._args = args
        self._kwargs = kwargs

    def __str__(self) -> str:
        args = [as_value(v) for v in self._args]
        kwargs = {k: as_value(v) for k, v in self._kwargs.items()}
        lparams = LazyArgumentsAndKeywords(args, kwargs)
        return f"{self._co}({lparams})"

    def __getattr__(self, name: str) -> Attr:
        # if name == "emit":
        #     raise AttributeError(name)
        return Attr(name, co=self)

    def __getitem__(self, name: str) -> "Getitem":
        return Getitem(name, co=self)

    @property
    def name(self) -> str:
        return str(self._co)

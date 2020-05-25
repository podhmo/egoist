from __future__ import annotations
import typing as t
from functools import partial, update_wrapper
from .app import App

if t.TYPE_CHECKING:
    from argparse import _SubParsersAction, ArgumentParser
    from prestring.codeobject import Symbol

AnyFunction = t.Callable[..., t.Any]
T = t.TypeVar("T")
DirectiveT = t.TypeVar("DirectiveT", bound="Directive")


class Directive:
    def __init__(
        self,
        define_fn: t.Callable[..., AnyFunction],
        *,
        name: str,
        requires: t.List[str],
        parameterized: bool,  # fixme: this is too implicit
    ) -> None:
        self.name = name
        self.__call__ = define_fn
        self.requires = requires
        self.parameterized = parameterized

        self.seen: bool = False

    def register(self, app: App, *args: t.Any, **kwargs: t.Any) -> t.Any:
        if not self.parameterized:
            return self.__call__(app, *args, **kwargs)

        def _register(target_fn: AnyFunction) -> AnyFunction:
            if not self.seen:
                self.seen = True

            return self.__call__(app, target_fn, *args, **kwargs)

        return _register

    def includeme(self, app: App) -> None:
        """callback for app.include()"""
        from miniconfig import PHASE1_CONFIG

        # for information used by describe()
        directive = partial(self.register)
        update_wrapper(directive, self.__call__)
        app.add_directive(self.name, directive)

        def _include() -> None:
            if not self.seen or not self.requires:
                return

            seen = app._aggressive_import_cache
            for path in self.requires:
                if path in seen:
                    continue
                app.include(path)

        app.action(self.name, _include, order=PHASE1_CONFIG)


def directive(
    directive_fn: t.Optional[t.Callable[..., t.Any]] = None,
    *,
    name: str,
    requires: t.List[str],
    factory: t.Type[DirectiveT] = Directive,  # type: ignore
    parameterized: bool = True,
) -> t.Callable[..., DirectiveT]:
    def _directive(directive_fn: t.Callable[..., t.Any]) -> DirectiveT:
        ob = factory(
            directive_fn, name=name, requires=requires, parameterized=parameterized
        )
        update_wrapper(ob, directive_fn)
        return ob

    return _directive


@directive(name="define_cli", requires=["egoist.generators.clikit"])
def define_cli(app: App, fn: AnyFunction, kit: str) -> AnyFunction:
    app.registry.generators[kit].append(fn)
    app.registry._task_list.append(fn.__name__)
    return fn


@directive(name="define_struct_set", requires=["egoist.generators.structkit"])
def define_struct_set(app: App, fn: AnyFunction, kit: str) -> AnyFunction:
    app.registry.generators[kit].append(fn)
    app.registry._task_list.append(fn.__name__)
    return fn


@directive(name="define_file", requires=["egoist.generators.filekit"])
def define_file(
    app: App,
    fn: AnyFunction,
    kit: str,
    *,
    rename: t.Optional[str] = None,
    suffix: str = "",
) -> AnyFunction:
    if rename is not None:
        fn._rename = rename  # type: ignore
    elif suffix:
        fn._rename = f"{fn.__name__}{suffix}"  # type: ignore
    app.registry.generators[kit].append(fn)
    app.registry._task_list.append(fn.__name__)
    return fn


@directive(name="define_dir", requires=["egoist.generators.dirkit"])
def define_dir(
    app: App, fn: AnyFunction, kit: str, *, rename: t.Optional[str] = None,
) -> AnyFunction:
    if rename is not None:
        fn._rename = rename  # type: ignore
    app.registry.generators[kit].append(fn)
    app.registry._task_list.append(fn.__name__)
    return fn


_global_subparsers: t.Optional[_SubParsersAction] = None


@directive(name="add_subcommand", requires=[], parameterized=False)
def add_subcommand(
    app: App,
    setup_parser: t.Callable[[App, ArgumentParser, AnyFunction], None],
    *,
    fn: AnyFunction,
) -> AnyFunction:
    """register subcommands"""
    global _global_subparsers
    subparsers = _global_subparsers
    if subparsers is None:
        subparsers = app.cli_parser.add_subparsers(
            title="subcommands", dest="subcommand"
        )
        subparsers.required = True
        _global_subparsers = subparsers

    sub_parser = subparsers.add_parser(
        fn.__name__, help=fn.__doc__, formatter_class=app.cli_parser.formatter_class
    )
    setup_parser(app, sub_parser, fn)
    return fn


@directive(name="shared", requires=[], parameterized=False)
def shared(app: App, fn: t.Callable[..., T]) -> AnyFunction:
    from functools import wraps

    name = f"{fn.__module__}:{fn.__name__}"

    def _return_fake() -> Symbol:
        from prestring.codeobject import Symbol

        return Symbol(name)

    @wraps(fn)
    def _cached(*args: t.Any, **kwargs: t.Any) -> T:
        from egoist.runtime import get_component

        return t.cast(T, get_component(name, *args, **kwargs))

    app.register_factory(name, fn)
    app.register_dryurn_factory(name, _return_fake)

    return _cached

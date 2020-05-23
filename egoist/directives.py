import typing as t
from functools import partial, update_wrapper
from .app import App, _noop

AnyFunction = t.Callable[..., t.Any]
T = t.TypeVar("T")


class Directive:
    def __init__(
        self, define_fn: AnyFunction, *, name: str, requires: t.List[str]
    ) -> None:
        self.define_fn = define_fn
        self.seen: bool = False
        self.name = name
        self.requires = requires

    @property
    def __call__(self) -> AnyFunction:
        return self.define_fn

    def register(self, app: App, *args, **kwargs) -> AnyFunction:
        def _register(target_fn: AnyFunction) -> AnyFunction:
            if not self.seen:
                self.seen = True
            self.define_fn(app, target_fn, *args, **kwargs)
            return target_fn

        return _register

    def includeme(self, app: App) -> None:
        """callback for app.include()"""
        # for information used by describe()
        directive = partial(self.register)
        update_wrapper(directive, self.define_fn)
        app.add_directive(self.name, directive)

        def _include() -> None:
            if not self.seen or not self.requires:
                return

            seen = app._aggressive_import_cache
            for path in self.requires:
                if path in seen:
                    continue
                app.include(path)

        app.action(self.name, _include)


def directive(
    directive_fn: t.Optional[t.Callable[..., t.Any]] = None,
    *,
    name: str,
    requires: t.List[str],
):
    def _directive(directive_fn: t.Callable[..., t.Any]):
        ob = Directive(directive_fn, name=name, requires=requires)
        update_wrapper(ob, directive_fn)
        return ob

    return _directive


_has_subparser = False


def add_subcommand(app: App) -> None:
    """register subcommands"""
    global _has_subparser
    if _has_subparser:
        return
    _has_subparser = True

    import argparse

    parser = app.cli_parser
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")
    subparsers.required = True

    def _add_subcommand(
        app: App,
        setup_parser: t.Callable[[App, argparse.ArgumentParser, AnyFunction], None],
        *,
        fn: AnyFunction,
    ) -> None:
        sub_parser = subparsers.add_parser(
            fn.__name__, help=fn.__doc__, formatter_class=parser.formatter_class
        )
        setup_parser(app, sub_parser, fn)

    app.add_directive("add_subcommand", _add_subcommand)


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


def shared(app: App) -> None:
    name = "shared"

    def _register_shared(app: App, fn: t.Callable[..., T]) -> AnyFunction:
        from functools import partial
        from prestring.codeobject import Symbol

        name = f"{fn.__module__}:{fn.__name__}"
        app.register_factory(name, fn)
        app.register_dryurn_factory(name, partial(Symbol, name))

        def cached(*args: t.Any, **kwargs: t.Any) -> T:
            from egoist.runtime import get_component

            return t.cast(T, get_component(name, *args, **kwargs))

        return cached

    app.add_directive(name, _register_shared)

    # for conflict check
    app.action(name, _noop)

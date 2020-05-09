from __future__ import annotations
import typing as t
import typing_extensions as tx
import dataclasses
from collections import defaultdict
import logging
from miniconfig import Configurator as _Configurator
from miniconfig import Context as _Context
from miniconfig.exceptions import ConfigurationError
from .langhelpers import reify

logger = logging.getLogger(__name__)


class SettingsDict(tx.TypedDict):
    rootdir: str
    here: str


@dataclasses.dataclass
class Registry:
    generate_settings: t.Dict[str, t.List[t.Callable[..., t.Any]]] = dataclasses.field(
        default_factory=lambda: defaultdict(list)
    )


class Context(_Context):
    @reify
    def registry(self) -> Registry:
        return Registry()

    committed: t.ClassVar[bool] = False


class App(_Configurator):
    context_factory = Context

    @property
    def registry(self) -> Registry:
        return self.context.registry  # type: ignore

    def commit(self) -> None:
        # only once
        if self.context.committed:  # type: ignore
            return

        self.context.committed = True  # type: ignore
        logger.debug("commit")
        super().commit()

    def describe(self) -> None:
        self.commit()

        import json
        import inspect

        defs = {}
        for kit, fns in self.registry.generate_settings.items():
            for fn in fns:
                name = f"{fn.__module__}.{fn.__name__}".replace("__main__.", "")
                summary = (inspect.getdoc(fn) or "").strip().split("\n", 1)[0]
                defs[name] = {"doc": summary, "generator": kit}
        d = {"definitions": defs}
        print(json.dumps(d, indent=2, ensure_ascii=False))

    def generate(
        self,
        *,
        rootdir: t.Optional[str] = None,
        targets: t.Optional[t.List[str]] = None,
    ) -> None:
        self.commit()

        import pathlib

        if rootdir is not None:
            root_path: pathlib.Path = pathlib.Path(rootdir)
        else:
            here = self.settings["here"]
            rootdir = self.settings["rootdir"]
            root_path = pathlib.Path(here).parent / rootdir

        for kit, fns in self.registry.generate_settings.items():
            generate_or_module = self.maybe_dotted(kit)
            if callable(generate_or_module):
                generate = generate_or_module
            elif hasattr(generate_or_module, "generate"):
                generate = generate_or_module.generate  # type: ignore
            else:
                # TODO: genetle error message
                raise ConfigurationError("{kit!r} is not callable")
            generate({fn.__name__: fn for fn in fns}, root=root_path)

    def run(self, argv: t.Optional[t.List[str]] = None) -> t.Any:
        import argparse
        from egoist.internal.logutil import logging_setup

        parser = argparse.ArgumentParser(
            formatter_class=type(
                "_HelpFormatter",
                (argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter),
                {},
            )
        )
        parser.print_usage = parser.print_help  # type: ignore
        subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")
        subparsers.required = True

        fn = self.describe
        sub_parser = subparsers.add_parser(
            fn.__name__, help=fn.__doc__, formatter_class=parser.formatter_class
        )
        sub_parser.set_defaults(subcommand=fn)

        fn = self.generate
        sub_parser = subparsers.add_parser(
            fn.__name__, help=fn.__doc__, formatter_class=parser.formatter_class
        )
        sub_parser.add_argument("--rootdir", required=False, help="-")
        # todo: scan modules in show_help only
        sub_parser.add_argument(
            "targets",
            nargs="*",
            choices=[[]] + list(fn.__name__ for fns in self.registry.generate_settings.values() for fn in fns),  # type: ignore
        )
        sub_parser.set_defaults(subcommand=fn)

        activate = logging_setup(parser)
        args = parser.parse_args(argv)
        params = vars(args).copy()
        activate(params)
        subcommand = params.pop("subcommand")
        return subcommand(**params)

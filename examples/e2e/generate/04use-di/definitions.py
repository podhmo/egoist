from __future__ import annotations
from egoist.internal.graph import Builder
from egoist import runtime
from magicalimport import import_module

internal = import_module("./internal.py", here=__file__)


def wire_example(*, grumby: bool = False) -> None:
    """
    google/wire event examples
    """
    from egoist.generate.clikit import clikit
    from egoist.go import di

    with runtime.generate(clikit) as m:
        b = Builder()

        b.add_node(**di.parse(internal.NewMessage))
        b.add_node(**di.parse(internal.NewGreeter))
        b.add_node(**di.parse(internal.NewEvent))

        g = b.build()

        primitives = di.primitives(g, locals())
        event = di.inject(m, g, variables=primitives)
        m.stmt(event.Start())


if __name__ == "__main__":
    runtime.main(name=__name__, here=__file__, root="cmd")

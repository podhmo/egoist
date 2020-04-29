from __future__ import annotations
from egoist.internal.graph import Builder
from egoist import runtime
from magicalimport import import_module

internal = import_module("./internal.py", here=__file__)
h = import_module("./helpers.py", here=__file__)


def wire_example(*, grumby: bool = False) -> None:
    """google/wire event examples"""
    from egoist.generate.clikit import clikit

    with runtime.generate(clikit) as m:
        b = Builder()

        b.add_node(**h.parse(internal.NewMessage))
        b.add_node(**h.parse(internal.NewGreeter))
        b.add_node(**h.parse(internal.NewEvent))

        g = b.build()
        kwargs = locals()  # xxx
        variables = {
            node.uid: kwargs[node.name] for node in g.nodes if node.is_primitive
        }

        event = h.inject(m, g, variables=variables)
        m.stmt(event.Start())


if __name__ == "__main__":
    runtime.main(name=__name__, here=__file__, root="cmd")

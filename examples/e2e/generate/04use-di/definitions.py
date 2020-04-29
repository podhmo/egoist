from __future__ import annotations
from egoist.internal.graph import Builder
from egoist import runtime
from magicalimport import import_module

internal = import_module("./internal.py", here=__file__)
h = import_module("./helpers.py", here=__file__)


def wire_example() -> None:
    """google/wire event examples"""
    from egoist.generate.clikit import clikit

    with runtime.generate(clikit) as m:
        b = Builder()

        b.add_node(**h.parse(internal.NewMessage))
        b.add_node(**h.parse(internal.NewGreeter))
        b.add_node(**h.parse(internal.NewEvent))

        g = b.build()
        component = h.emit(m, g)
        m.stmt(component.Start())


if __name__ == "__main__":
    runtime.main(name=__name__, here=__file__, root="cmd")

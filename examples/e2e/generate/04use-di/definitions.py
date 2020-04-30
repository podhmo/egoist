from __future__ import annotations
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
        b = di.Builder()

        b.add_provider(internal.NewMessage)
        b.add_provider(internal.NewGreeter)
        b.add_provider(internal.NewEvent)

        injector = b.build(variables=locals())
        event = injector.inject(m)
        m.stmt(event.Start())


if __name__ == "__main__":
    runtime.main(name=__name__, here=__file__, root="cmd")

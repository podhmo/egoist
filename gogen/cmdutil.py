from handofcats import as_subcommand, Config
from handofcats import get_default_multi_driver


def is_marked_subcommand(fn):
    d = get_default_multi_driver()
    return fn in d.functions


__all__ = ["as_subcommand", "Config"]

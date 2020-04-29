from handofcats import as_command
from handofcats import as_subcommand
from handofcats import Config
from handofcats import get_default_multi_driver


def is_marked_subcommand(fn):
    d = get_default_multi_driver()
    return fn in d.functions


__all__ = ["as_command", "as_subcommand", "Config"]

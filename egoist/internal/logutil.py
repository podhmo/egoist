import typing as t
from functools import partial
import os
import sys
import argparse
import logging


def logging_setup(
    parser: argparse.ArgumentParser, *, debug: bool = False
) -> t.Callable[[t.Dict[str, t.Any]], None]:
    logging_levels = list(logging._nameToLevel.keys())
    parser.add_argument("--logging", choices=logging_levels, default=None)
    return partial(logging_activate, debug=debug)


def logging_activate(
    params: t.Dict[str, t.Any],
    *,
    debug: bool = False,
    logging_level: t.Optional[int] = None,
    logging_format: t.Optional[str] = None,
    logging_stream: t.Optional[t.IO[str]] = None,
    logging_time: t.Optional[str] = None,  # "relative", "asctime", None
) -> None:
    time_format_map = {
        "relative": "relative:%(relativeCreated)s	",
        "asctime": "asctime:%(asctime)s	",
        None: "",
    }
    if os.environ.get("LOGGING_TIME"):
        logging_time = os.environ["LOGGING_TIME"]

    logging_format = (
        logging_format
        or f"level:%(levelname)s	{time_format_map.get(logging_time, '')}message:%(message)-40s	name:%(name)sL%(lineno)s"
    )

    logging_level = logging_level or logging.INFO
    if debug or bool(os.environ.get("DEBUG", "").strip()):
        logging_level = logging.DEBUG
        print(
            "** {where}: DEBUG=1, activate logging **".format(where=__name__),
            file=sys.stderr,
        )

    if os.environ.get("LOGGING_LEVEL"):
        logging_level = logging._nameToLevel.get(os.environ["LOGGING_LEVEL"].upper())
    if os.environ.get("LOGGING_FORMAT"):
        logging_format = os.environ["LOGGING_FORMAT"]
    if os.environ.get("LOGGING_STREAM"):
        logging_stream = getattr(sys, os.environ["LOGGING_STREAM"])

    if "logging" in params:
        level = params.pop("logging", None)
        if level is not None:
            logging_level = level

    logging.basicConfig(
        level=logging_level, format=logging_format, stream=logging_stream,
    )
    logging.getLogger("metashape.analyze.walker").setLevel(logging.WARNING)

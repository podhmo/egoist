from __future__ import annotations
import typing as t
import typing_extensions as tx
import logging
from egoist.app import App

logger = logging.getLogger(__name__)

# for add_server_process()'s params parameter
# using these functions, like below
#
# `app.add_server_process("xxxrpc --port {port}", params={"port": find_free_port})`


class LazyParam(tx.Protocol):
    def __call__(self, app: App) -> str:
        ...


def find_free_port(app: App) -> str:
    return str(_find_free_port(host="0.0.0.0"))


def create_sentinel_file(app: App) -> str:
    return _create_sentinel_file(suffix=".sentinel")


def constant(value: str) -> LazyParam:
    return lambda app: value


def _find_free_port(host: str = "0.0.0.0") -> int:
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        sock.listen(1)
        name, port = sock.getsockname()  # type: t.Tuple[str, int]
    return port


def _create_sentinel_file(suffix: t.Optional[str] = None) -> str:
    import tempfile

    fd, sentinel = tempfile.mkstemp(suffix=suffix)
    logger.debug("create sentinel %s", sentinel)
    return sentinel

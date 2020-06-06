import typing as t
import logging
from egoist.app import App

logger = logging.getLogger(__name__)

# for add_server_process()'s params parameter
# using these functions, like below
#
# `app.add_server_process("xxxrpc --port {port}", params={"port": find_free_port})`


def find_free_port(app: App, *, host: str = "0.0.0.0") -> int:
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        sock.listen(1)
        name, port = sock.getsockname()  # type: t.Tuple[str, int]
    return port


def create_sentinel_file(app: App, *, suffix: str = ".sentinel") -> str:
    import tempfile

    fd, sentinel = tempfile.mkstemp(suffix=suffix)
    logger.debug("create sentinel %s", sentinel)
    return sentinel

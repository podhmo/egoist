from __future__ import annotations
import typing as t
import typing_extensions as tx
import os
import time
import pathlib
import subprocess
import logging


logger = logging.getLogger(__name__)


class ConnectionChecker(tx.Protocol):
    def ping(self) -> bool:
        """is connected?"""
        ...

    def pong(self) -> bool:
        """reply"""
        ...


class FileConnectionChecker:  # ConnectionChecker
    def __init__(self, sentinel: str):
        self.sentinel = sentinel

    def ping(self) -> bool:
        return not pathlib.Path(self.sentinel).exists()

    def pong(self) -> bool:
        sentinel = self.sentinel
        if pathlib.Path(sentinel).exists():
            logger.info("remove sentinel %s", sentinel)
            pathlib.Path(sentinel).unlink()
            return True
        return False


def spawn_with_connection(
    argv: t.List[str],
    *,
    sentinel: str,
    retries: t.List[float] = [0.1, 0.2, 0.2, 0.4, 0.8, 1.6, 3.2, 6.4],
    check: bool = True,
    environ: t.Optional[t.Dict[str, str]] = None,
    create_connection_checker: t.Callable[
        [str], ConnectionChecker
    ] = FileConnectionChecker,
) -> t.Tuple[subprocess.Popen[str], ConnectionChecker]:
    if check and (environ is None or sentinel not in list(environ.values())):
        assert sentinel in argv

    if environ is not None:
        environ.update(os.environ)

    logger.info("spawn server process, %s", " ".join(argv))
    p = subprocess.Popen(argv, text=True, env=environ)

    checker = create_connection_checker(sentinel)

    if not check:
        return p, checker

    try:
        start_time = time.time()
        end_time = None

        for wait_time in retries:
            if checker.ping():
                end_time = time.time()
                logger.debug("connected")
                break

            logger.debug("wait: %f", wait_time)
            time.sleep(wait_time)  # todo: backoff

        if end_time is None:
            raise TimeoutError(f"{time.time() - start_time} sec passed, {p.args!r}")
        return p, checker
    except Exception as exc:
        logger.warning("hmm %r, kill process", exc)
        p.kill()  # kill?
        raise

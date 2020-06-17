from __future__ import annotations
import typing as t
import logging
from egoist.app import App

AnyFunction = t.Callable[..., t.Any]
if t.TYPE_CHECKING:
    from .lazyparams import LazyParam
logger = logging.getLogger(__name__)


def add_server_process(app: App) -> None:
    def _define(
        app: App,
        fmt: str,
        *,
        name: str,
        urlfmt: str = "http://{host}:{port}",
        host: str = "127.0.0.1",
        port: t.Optional[t.Union[int, str]] = None,
        params: t.Optional[t.Dict[str, LazyParam]] = None,
        env: t.Optional[t.Dict[str, LazyParam]] = None,
        nowait: bool = False,
    ) -> None:
        app.include("egoist.ext.serverprocess.components.discovery")
        app.include("egoist.ext.serverprocess.components.httpclient")

        def _register() -> None:
            nonlocal host
            nonlocal port

            import shlex
            import atexit
            from .components.discovery import get_discovery
            from .lazyparams import find_free_port, create_sentinel_file

            if app.registry.dry_run:
                kwargs: t.Dict[str, t.Any] = {k: "xxx" for k in (params or {}).keys()}
                environ = {k: "xxx" for k in (env or {}).keys()}
                port = "xxx"
                sentinel = "xxx"
            else:
                kwargs = {k: fn(app) for k, fn in (params or {}).items()}
                environ = {k: fn(app) for k, fn in (env or {}).items()}
                if port is None:
                    port = kwargs.get("port") or find_free_port(app)
                elif "port" not in kwargs:
                    kwargs["port"] = port

                if "host" in kwargs:
                    host = kwargs["host"]
                elif "host" not in kwargs:
                    kwargs["host"] = host

                sentinel = (
                    None
                    if nowait
                    else (  # xxx
                        kwargs.get("sentinel")
                        or environ.get("SENTINEL")
                        or create_sentinel_file(app)
                    )
                )

            argv = shlex.split(fmt.format(**kwargs))
            url = urlfmt.format(host=host, port=port)
            get_discovery().register(name, url=url)

            if app.registry.dry_run:
                logger.info("dry run, skip starting server process, %s", name)
                return

            from .spawn import spawn_with_connection

            p, _ = spawn_with_connection(
                argv, sentinel=sentinel, environ=environ, check=not nowait
            )

            def _shutdown() -> None:  # xxx:
                logger.info("terminate %s", name)
                with p:
                    p.terminate()

            atexit.register(_shutdown)

        app.action(("add_server_process", name), _register)

    app.add_directive("add_server_process", _define)

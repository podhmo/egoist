import typing as t
import logging
from egoist.app import App

logger = logging.getLogger(__name__)


def add_server_process(app: App):
    def _define(
        app: App,
        fmt: str,
        *,
        name: str,
        urlfmt: str = "http://{host}:{port}",
        host: str = "127.0.0.1",
        sentinel: t.Optional[str] = None,
        port: t.Optional[int] = None,
        params: t.Optional[t.Dict[str, t.Callable[[], object]]] = None,
    ):
        app.include("egoist.ext.serverprocess.components.discovery")
        app.include("egoist.ext.serverprocess.components.httpclient")

        def _register():
            nonlocal host
            nonlocal port

            import shlex
            import atexit
            from .components.discovery import get_discovery
            from .lazyparams import find_free_port, create_sentinel_file

            if app.registry.dry_run:
                kwargs = {k: "xxx" for k, fn in (params or {}).items()}
                port = "xxx"
                sentinel = "xxx"
            else:
                kwargs = {k: fn(app) for k, fn in (params or {}).items()}
                if port is None:
                    port = kwargs.get("port") or find_free_port(app)
                if "host" in kwargs:
                    host = kwargs["host"]
                if "sentinel" in kwargs:
                    sentinel = kwargs.get("sentinel") or create_sentinel_file(app)

            argv = shlex.split(fmt.format(**kwargs))
            url = urlfmt.format(host=host, port=port)
            get_discovery().register(name, url=url)

            if app.registry.dry_run:
                logger.info("dry run, skip starting server process, %s", name)
                return

            from .spawn import spawn_with_connection

            p, _ = spawn_with_connection(argv, sentinel=sentinel)

            def _shutdown():  # xxx:
                logger.info("terminate %s", name)
                with p:
                    p.terminate()

            atexit.register(_shutdown)

        app.action(("add_server_process", name), _register)

    app.add_directive("add_server_process", _define)

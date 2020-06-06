from __future__ import annotations
from egoist.app import create_app, SettingsDict, parse_args
from egoist.go.types import GoError


settings: SettingsDict = {"rootdir": "cmd/", "here": __file__}
app = create_app(settings)

app.include("egoist.directives.define_cli")


@app.define_cli("egoist.generators.clikit:walk")
def gofmtrpc(*, addr: str = ":9999", sentinel: str = "") -> GoError:
    """gofmtrpc with JSONRPC"""
    from egoist.generators.clikit import runtime, clikit

    with runtime.generate(clikit) as m:
        gofmtrpc_pkg = m.import_("github.com/podhmo/egoist/gofmtrpc")
        m.return_(gofmtrpc_pkg.Run(addr, sentinel))


if __name__ == "__main__":
    for argv in parse_args(sep="-"):
        app.run(argv)

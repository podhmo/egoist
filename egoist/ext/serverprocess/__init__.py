from egoist.app import App


def includeme(app: App) -> None:
    app.include("./directives:add_server_process")  # for add_server_process()

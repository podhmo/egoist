from __future__ import annotations
from egoist.app import App


def includeme(app: App):
    print("INCLUDE", "xxx")
    app.registry.settings["xxx"] = "xxx"

from __future__ import annotations
import typing as t
from egoist.app import App

if t.TYPE_CHECKING:
    from requests import Session
    from egoist.internal.fake import Symbol

NAME = __name__


def get_http_client() -> Session:
    from egoist.runtime import get_component_factory

    return get_component_factory(NAME)()


def _create_http_client() -> Session:
    import requests

    return requests.Session()


def _create_fake_http_client() -> Symbol:
    from egoist.internal import fake

    return fake.Symbol(__name__)


def includeme(app: App) -> None:
    app.register_factory(NAME, _create_http_client)
    app.register_dryurn_factory(NAME, _create_fake_http_client)

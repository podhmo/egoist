from __future__ import annotations
import typing as t
from datetime import datetime
from openapi.runtime import API
import objects

if t.TYPE_CHECKING:
    from egoist.app import App
# todo: security


def login(body: LoginUserRequest) -> t.List[UserResponse]:
    # "401": {
    #   "description": "Unauthorized"
    # },
    # "422": {
    #   "description": "Unexpected error",
    #   "schema": {
    #     "$ref": "#/definitions/GenericErrorModel"
    #   }
    # }
    pass


class LoginUserRequest:
    """Credentials to use"""

    user: objects.LoginUser


class UserResponse:
    user: objects.User


def CreateUser(body: NewUserRequest) -> UserResponse:
    """Register a new user

    Register a new user"""
    # "201": {
    #   "description": "OK",
    #   "schema": {
    #     "$ref": "#/definitions/UserResponse"
    #   }
    # },
    # "422": {
    #   "description": "Unexpected error",
    #   "schema": {
    #     "$ref": "#/definitions/GenericErrorModel"
    #   }
    # }
    pass


class NewUserRequest:
    user: objects.NewUser


def get_current_user() -> UserResponse:
    """Get current user

    Gets the currently logged-in user"""
    # "401": {
    #   "description": "Unauthorized"
    # },
    # "422": {
    #   "description": "Unexpected error",
    #   "schema": {
    #     "$ref": "#/definitions/GenericErrorModel"
    #   }
    # }
    pass


def update_current_user(body: UpdateUserRequest) -> UserResponse:
    """Update current user

    Updated user information for current user"""
    # "401": {
    #   "description": "Unauthorized"
    # },
    # "422": {
    #   "description": "Unexpected error",
    #   "schema": {
    #     "$ref": "#/definitions/GenericErrorModel"
    #   }
    # }
    pass


class UpdateUserRequest:
    user: objects.UpdateUser


def includeme(app: App) -> None:
    api = API()
    api.post("/users/login", metadata={"tags": ["User and Authentication"]})(login)

    api.post("/users", metadata={"tags": ["User and Authentication"]})(CreateUser)
    api.get("/users", metadata={"tags": ["User and Authentication"]})(get_current_user)
    api.put("/users", metadata={"tags": ["User and Authentication"]})(
        update_current_user
    )
    app.context.api = api  # xxx:

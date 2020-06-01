from __future__ import annotations
import typing as t
from datetime import datetime
from openapi.runtime import App

# todo: security
app = App()


# class Article:
#     author: Profile
#     body: str
#     # createdAt: datetime
#     description: str
#     favorited: bool
#     favoritesCount: int
#     slug: str
#     tagList: t.List[str]
#     title: str


class LoginUser:
    email: str
    password: str  # format=password


class User:
    email: str
    token: str
    username: str
    bio: str
    image: str


class UpdateUser:
    email: str
    token: str
    username: str
    bio: str
    image: str


@app.post("/users/login", metadata={"tags": ["User and Authentication"]})
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

    user: LoginUser


class UserResponse:
    user: User


@app.get("/users/login", metadata={"tags": ["User and Authentication"]})
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


@app.put("/users/login", metadata={"tags": ["User and Authentication"]})
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
    user: UpdateUser

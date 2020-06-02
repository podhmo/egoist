from __future__ import annotations
import typing as t
from datetime import datetime


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


class NewUser:
    username: str
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

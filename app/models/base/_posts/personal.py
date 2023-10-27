# Copyright (C) 2023 David Shiko
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
from enum import IntEnum

from app.db import crud
from .shared import PostBase, PostDC, PostProtocol

if TYPE_CHECKING:
    from psycopg2.extensions import connection as pg_ext_connection
    from app.models.users import UserInterface


class PostInterface(ABC, PostProtocol,):

    class PostFlag(ABC):
        DECLINE: int
        ACCEPT: int

    CRUD: crud.posts.PersonalPost

    @abstractmethod
    def __repr__(self) -> str:
        ...

    @classmethod
    @abstractmethod
    def create(
            cls,
            author: UserInterface,
            message_id: int,
    ) -> PostInterface:
        """Sql is different for public and personal post samples."""
        ...

    @classmethod
    @abstractmethod
    def read_user_posts(cls, user: UserInterface, ) -> list[PostInterface]:
        ...

    @classmethod
    @abstractmethod
    def delete(cls, post_id: int, connection: pg_ext_connection, ) -> None:
        ...


class Post(PostDC, PostInterface, ):

    class PostFlag(IntEnum):
        DECLINE = 0
        ACCEPT = 1

    CRUD = crud.posts.PersonalPost
    PostBase = PostBase

    def __init__(self, author: UserInterface, message_id: int, post_id: int, ) -> None:
        super().__init__(author=author, post_id=post_id, message_id=message_id, )

    def __repr__(self) -> str:
        d = {
            'self': object.__repr__(self),
            'author': self.author,
            'post_id': self.post_id,
            'message_id': self.message_id
        }
        return repr({k: v for k, v in d.items() if v is not None}) + '\n'

    @classmethod
    def create(
            cls,
            author: UserInterface,
            message_id: int,
    ) -> PostInterface:
        return cls.PostBase.create(cls=cls, author=author, message_id=message_id, )

    @classmethod
    def read_user_posts(cls, user: UserInterface, ) -> list[PostInterface]:
        posts = cls.CRUD.read_user_posts(tg_user_id=user.tg_user_id, connection=user.connection, )
        return [cls(author=user, post_id=post['post_id'], message_id=post['message_id'], ) for post in posts]

    @classmethod
    def delete(cls, post_id: int, connection: pg_ext_connection, ):
        return cls.CRUD.delete(post_id=post_id, connection=connection, )

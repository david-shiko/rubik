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
from abc import ABC, abstractmethod
from enum import IntEnum
from typing import TYPE_CHECKING, Type

from app.db import crud
from .shared import PostBase, PostDC, PostProtocol

if TYPE_CHECKING:
    from app.models.users import UserInterface


class Status(IntEnum):
    PENDING = 0
    READY_TO_RELEASE = 1
    RELEASED = 2


class PostInterface(ABC, PostProtocol, ):
    Status: Status
    CRUD: crud.posts.PublicPost

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

    @abstractmethod
    def update_status(
            self,
            # Ignore cuz mypy uses status from PostInterface, not from required module scope
            status: Status,  # type: ignore[valid-type]
    ) -> None:
        ...

    @abstractmethod
    def update_votes_count(self, ) -> None:
        ...


class Post(PostDC, PostInterface, ):

    CRUD: Type[crud.posts.PublicPost] = crud.posts.PublicPost
    PostBase = PostBase
    Status = Status

    def __init__(
            self,
            author: UserInterface,
            post_id: int,
            message_id: int,
            likes_count: int = 0,
            dislikes_count: int = 0,
            status: Status = Status.PENDING,
    ):
        super().__init__(author=author, post_id=post_id, message_id=message_id, )
        self.likes_count = likes_count
        self.dislikes_count = dislikes_count
        self.status = status  # Only public post has a status

    def __repr__(self) -> str:
        d = {
            'self': object.__repr__(self),
            'author': self.author,
            'message_id': self.message_id,
            'post_id': self.post_id,
            'likes_count': self.likes_count,
            'dislikes_count': self.dislikes_count,
            'status': self.status
        }
        return repr({k: v for k, v in d.items() if v is not None}) + '\n'

    @classmethod
    def create(
            cls,
            author: UserInterface,
            message_id: int,
    ) -> PostInterface:
        return cls.PostBase.create(cls=cls, author=author, message_id=message_id, )

    def update_status(self, status: Status, ) -> None:
        self.CRUD.update_status(
            post_id=self.post_id,
            connection=self.author.connection,
            status=status.value,
        )
        self.status = status

    def update_votes_count(self, ) -> None:
        self.CRUD.update_votes_count(
            post_id=self.post_id,
            likes_count=self.likes_count,
            dislikes_count=self.dislikes_count,
            connection=self.author.connection,
        )

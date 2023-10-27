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
from typing import TYPE_CHECKING, Protocol, Type, TypeVar

if TYPE_CHECKING:
    from app.db import crud
    from app.models.users import UserInterface


class PostProtocol(Protocol, ):
    author: UserInterface
    post_id: int
    message_id: int


class PostDC(PostProtocol, ):

    CRUD: crud.posts.PublicPost | crud.posts.PersonalPost

    def __init__(
            self,
            author: UserInterface,
            post_id: int,
            message_id: int,
    ):
        self.author = author
        self.post_id = post_id
        self.message_id = message_id


T = TypeVar('T', bound=PostDC, )  # Use T cuz PostBaseInterface is not a quite real interface


class PostBase:

    @staticmethod
    def create(
            cls: Type[T],
            author: UserInterface,
            message_id: int,
    ) -> T:
        """Sql is different for public and personal post samples."""
        newly_created_post_id = cls.CRUD.create(
            author=author.tg_user_id,
            message_id=message_id,
            connection=author.connection,
        )
        return cls(author=author, post_id=newly_created_post_id, message_id=message_id, )

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
from typing import TYPE_CHECKING, Protocol
from abc import ABC, abstractmethod

import app.db.crud.collections

if TYPE_CHECKING:
    from psycopg2.extensions import connection as pg_ext_connection
    import app.models.posts
    import app.models.users

"""This class not depends on other classes (not uses them)"""


class CollectionProtocol(Protocol, ):
    author: app.models.users.User
    collection_id: int
    posts: list[app.models.posts.PersonalPost] | None
    name: str


class CollectionInterface(CollectionProtocol, ABC):

    @classmethod
    @abstractmethod
    def create(cls, author: app.models.users.User, name: str, posts_ids: list[int], ) -> None:
        ...

    @classmethod
    @abstractmethod
    def get_defaults_names(cls, prefix: str, connection: pg_ext_connection, ) -> list[str]:
        ...


class Collection(CollectionInterface, ):
    CRUD = app.db.crud.collections.Collection
    DEFAULT_NAME: str = 'default'
    MAX_NAME_LEN: int = 25
    MAX_COLLECTIONS_COUNT: int = 10  # Not in use
    MAX_POSTS_COUNT: int = 10

    def __init__(
            self,
            author: app.models.users.User,
            collection_id: int,
            posts: list[app.models.posts.PersonalPost] | None = None,
            name: str = DEFAULT_NAME,
    ):
        self.author = author
        self.collection_id = collection_id
        self.name = name
        self.posts = posts or []
        self.posts_count = len(self.posts)

    @classmethod
    def create(
            cls,
            author: app.models.users.User,
            name: str,
            posts_ids: list[int],
    ) -> None:
        """
        Create collection and link to posts_ids
        Flow:
        1. Create collection itself.
        2. If exists - read existing collection id.
        3. Create m2m map of collection and passed posts_ids in params.
        """
        newly_created_collection_id = cls.CRUD.create(  # Returns None if already exists
            author=author.tg_user_id,
            name=name,
            connection=author.connection,
        )
        if newly_created_collection_id is None:  # if collection already exists (conflict returns "NULL")
            newly_created_collection_id = cls.CRUD.read_id_by_name(
                author=author.tg_user_id,
                name=name,
                connection=author.connection,
            )
        for post_id in posts_ids:
            cls.CRUD.create_2m2_collection_post(
                collection_id=newly_created_collection_id,
                post_id=post_id,
                connection=author.connection,
            )

    @classmethod
    def get_defaults_names(cls, prefix: str, connection: pg_ext_connection, ) -> list[str]:
        collections = cls.CRUD.read_defaults_names(connection=connection, prefix=prefix, )
        return collections

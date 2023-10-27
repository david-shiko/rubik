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

from app.models import base
from app.utils import raise_
from app import exceptions

if TYPE_CHECKING:
    from psycopg2.extensions import connection as pg_ext_connection

    from app.structures.base import CollectionDB
    from app.models import CollectionMapper
    from app.models.posts import PublicPostInterface, PersonalPostInterface 
    from app.models.users import UserInterface


class CollectionInterface(base.collections.CollectionInterface, ABC, ):
    Mapper: CollectionMapper

    @classmethod
    @abstractmethod
    def get_posts(
            cls,
            collection_id: int,
            author: UserInterface | None = None,
            connection: pg_ext_connection | None = None,
    ) -> list[PublicPostInterface | PersonalPostInterface]:
        ...

    @classmethod
    @abstractmethod
    def get_user_collections(cls, author: UserInterface, ) -> list[Collection]:
        ...

    @classmethod
    @abstractmethod
    def get_by_ids(cls, ids: list[int], user: UserInterface, ) -> list[Collection]:
        ...

    @classmethod
    @abstractmethod
    def db_to_cls(
            cls,
            raw_collection: CollectionDB,
            author: UserInterface | None = None,
    ) -> Collection:
        ...

    @classmethod
    @abstractmethod
    def get_defaults(
            cls,
            prefix: str,
            author: UserInterface,
    ) -> list[Collection]:
        ...


class Collection(base.collections.Collection, CollectionInterface, ):
    Mapper: CollectionMapper

    @classmethod
    def get_posts(
            cls,
            collection_id: int,
            author: UserInterface | None = None,
            connection: pg_ext_connection | None = None,
    ) -> list[PublicPostInterface | PersonalPostInterface]:
        connection = connection or (author and author.connection) or raise_(e=exceptions.ConnectionNotPassed)
        posts = []
        public_posts_raw = cls.CRUD.read_posts_public(
            collection_id=collection_id,
            connection=connection
        )
        posts.extend(
            cls.Mapper.PublicPost.dbs_to_cls(
                posts_rows=public_posts_raw,
                connection=connection,
            ), )
        personal_posts_raw = cls.CRUD.read_posts_personal(
            collection_id=collection_id,
            connection=connection,
        )
        posts.extend(
            cls.Mapper.PersonalPost.dbs_to_cls(
                posts_rows=personal_posts_raw,
                connection=connection,
            ), )
        return posts

    @classmethod
    def db_to_cls(
            cls,
            raw_collection: CollectionDB,
            author: UserInterface | None = None,
    ) -> Collection:
        return cls(
            author=author or cls.Mapper.User(tg_user_id=raw_collection['author'], ),
            collection_id=raw_collection['collection_id'],
            name=raw_collection['name'],
        )

    @classmethod
    def get_defaults(
            cls,
            prefix: str,
            author: UserInterface,
    ) -> list[Collection]:
        collections = []
        for raw_collection in cls.CRUD.read_defaults(connection=author.connection, prefix=prefix, ):
            collections.append(cls.db_to_cls(author=author, raw_collection=raw_collection, ))
        return collections

    @classmethod
    def get_user_collections(
            cls,
            author: UserInterface,
    ) -> list[Collection]:
        """Will not fill the posts because it's a separate table"""
        raw_collections = cls.CRUD.read_user_collections(author=author.tg_user_id, connection=author.connection, )
        collections = []
        for raw_collection in raw_collections:
            collections.append(cls.db_to_cls(raw_collection=raw_collection, author=author, ))
        return collections

    @classmethod
    def get_by_ids(
            cls,
            ids: list[int],
            user: UserInterface,
    ) -> list[Collection]:
        """Will not fill the posts because it's a separate table"""
        raw_collections = cls.CRUD.read_by_ids(ids=ids, connection=user.connection, )
        collections = []
        for raw_collection in raw_collections:
            if raw_collection['author'] == user.tg_user_id:
                author = user
            else:
                author = cls.Mapper.User(tg_user_id=raw_collection['author'], connection=user.connection, )
            collections.append(cls.db_to_cls(raw_collection=raw_collection, author=author, ))
        return collections

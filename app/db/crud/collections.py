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

import app.db.manager

if TYPE_CHECKING:
    from psycopg2.extensions import connection as pg_ext_connection
    import app.structures.base


class Collection:
    db = app.db.manager.Postgres

    @classmethod
    def create(cls, author: int, name: str, connection: pg_ext_connection, ) -> int:
        """Insert into table"""
        newly_create_id = cls.db.create(
            statement=cls.db.sqls.Collections.CREATE_COLLECTION,
            values=(author, name,),
            connection=connection,
        )
        return newly_create_id

    @classmethod
    def create_2m2_collection_post(cls, collection_id: int, post_id: int, connection: pg_ext_connection, ) -> None:
        """Insert into table"""
        return cls.db.create(
            statement=cls.db.sqls.Collections.CREATE_M2M_COLLECTIONS_POSTS,
            values=(collection_id, post_id,),
            connection=connection,
        )

    @classmethod
    def read_id_by_name(
            cls,
            author: int,
            name: str,
            connection: pg_ext_connection,
    ) -> int:
        collection_id = cls.db.read(
            statement=cls.db.sqls.Collections.READ_USER_COLLECTION_ID_BY_NAME,
            values=(author, name,),
            connection=connection,
        )
        return collection_id

    @classmethod
    def read_by_ids(
            cls,
            ids: list[int],
            connection: pg_ext_connection,
    ) -> list[app.structures.base.CollectionDB]:
        """Will not fill the posts because it's a separate table"""
        collections: list[app.structures.base.CollectionDB] = cls.db.read(
            statement=cls.db.sqls.Collections.READ_COLLECTIONS_BY_IDS,
            values=(tuple(ids),),  # list of ids should be tuple
            connection=connection,
            fetch='fetchall'
        )
        return collections

    @classmethod
    def read_user_collections(
            cls,
            author: int,
            connection: pg_ext_connection,
    ) -> list[app.structures.base.CollectionDB]:
        """Will not fill the posts because it's a separate table"""
        collections: list[app.structures.base.CollectionDB] = cls.db.read(
            statement=cls.db.sqls.Collections.READ_USER_COLLECTIONS,
            values=(author,),
            connection=connection,
            fetch='fetchall'
        )
        return collections

    @classmethod
    def read_posts_public(
            cls,
            collection_id: int,
            connection: pg_ext_connection,
    ) -> list[app.structures.base.PublicPostDB]:
        posts: list[app.structures.base.PersonalPostDB | app.structures.base.PublicPostDB] = cls.db.read(
            statement=cls.db.sqls.Collections.READ_PUBLIC_COLLECTION_POSTS,
            values=(collection_id,),
            connection=connection,
            fetch='fetchall'
        )
        return posts

    @classmethod
    def read_posts_personal(
            cls,
            collection_id: int,
            connection: pg_ext_connection,
    ) -> list[app.structures.base.PersonalPostDB]:
        posts: list[app.structures.base.PersonalPostDB | app.structures.base.PublicPostDB] = cls.db.read(
            statement=cls.db.sqls.Collections.READ_PERSONAL_COLLECTION_POSTS,
            values=(collection_id,),
            connection=connection,
            fetch='fetchall'
        )
        return posts

    @classmethod
    def read_defaults_names(cls, prefix: str, connection: pg_ext_connection, ) -> list[str]:
        result = cls.db.read(
            statement=cls.db.sqls.Collections.READ_DEFAULT_COLLECTION_NAMES,
            values=(app.config.BOT_ID, prefix,),
            connection=connection,
            fetch='fetchall',
        )
        return result

    @classmethod
    def read_defaults(
            cls,
            prefix: str,
            connection: pg_ext_connection,
    ) -> list[app.structures.base.CollectionDB]:
        result = cls.db.read(
            statement=cls.db.sqls.Collections.READ_DEFAULT_COLLECTIONS,
            values=(app.config.BOT_ID, prefix,),
            connection=connection,
            fetch='fetchall',
        )
        return result

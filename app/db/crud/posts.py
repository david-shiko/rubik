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
import app.structures.base

if TYPE_CHECKING:
    from psycopg2.extensions import connection as pg_ext_connection
    from app.models.posts import PublicPost as PublicPostModel
    import app.structures.base


class PublicPost:
    db = app.db.manager.Postgres

    @classmethod
    def read(cls, post_id: int, connection: pg_ext_connection) -> app.structures.base.PublicPostDB | None:
        post_row: app.structures.base.PublicPostDB | None = cls.db.read(
            statement=cls.db.sqls.PublicPosts.READ_PUBLIC_POST_BY_ID,
            values=(post_id,),
            connection=connection,
        )
        return post_row

    @classmethod
    def create(cls, author: int, message_id: int, connection: pg_ext_connection) -> int:
        """Create rows in both posts_base and public_posts tables. """
        public_post_id = cls.db.create(
            statement=cls.db.sqls.PublicPosts.CREATE_PUBLIC_POST,
            values=(author, message_id,),
            connection=connection,
        )

        return public_post_id

    @classmethod
    def update_votes_count(
            cls, post_id: int, likes_count: int, dislikes_count: int, connection: pg_ext_connection
    ) -> None:
        cls.db.update(
            statement=cls.db.sqls.PublicPosts.UPDATE_PUBLIC_POST_VOTES_COUNT,
            values=(likes_count, dislikes_count, post_id,),
            connection=connection,
        )

    @classmethod
    def update_status(cls, post_id: int, status: int, connection: pg_ext_connection) -> None:
        cls.db.update(
            statement=cls.db.sqls.PublicPosts.UPDATE_PUBLIC_POST_STATUS,
            values=(status, post_id,),
            connection=connection,
        )

    @classmethod
    def read_exclusive(
            cls, tg_user_id: int, status: int, connection: pg_ext_connection
    ) -> app.structures.base.PublicPostDB | None:
        post_row: app.structures.base.PublicPostDB | None = cls.db.read(
            statement=cls.db.sqls.PublicPosts.READ_EXCLUSIVE_PUBLIC_POST,
            values=(status, tg_user_id,),
            connection=connection,
        )
        return post_row

    @classmethod
    def read_mass(cls, status: int, connection: pg_ext_connection) -> app.structures.base.PublicPostDB | None:
        """
        Read post to send to group of users.
        """
        post_row: app.structures.base.PublicPostDB | None = cls.db.read(
            statement=cls.db.sqls.PublicPosts.READ_PUBLIC_POST_MASS,
            values=(status,),
            connection=connection,
        )
        return post_row

    @classmethod
    def read_voted_users_ids(cls, post_id: int, connection: pg_ext_connection) -> list[int]:
        """Read ids of voted users for this post"""
        return cls.db.read(
            statement=cls.db.sqls.PublicVotes.READ_USERS_IDS_VOTED_FOR_PUBLIC_POST,  # Another sql cls
            values=(post_id,),
            connection=connection,
            fetch='fetchall',
        )

    @classmethod
    def read_public_posts_by_status(
            cls,
            status: PublicPostModel.Status,
            connection: pg_ext_connection,
    ) -> list[app.structures.base.PublicPostDB]:
        """RETURNS posts with status 0 ("PENDING") from DB"""
        raw_posts = cls.db.read(
            statement=cls.db.sqls.PublicPosts.READ_PUBLIC_POSTS_BY_STATUS,
            values=(status, ),
            connection=connection,
            fetch='fetchall',
        )
        return raw_posts


class PersonalPost:
    db = app.db.manager.Postgres

    @classmethod
    def read_user_posts(
            cls,
            tg_user_id: int,
            connection: pg_ext_connection,
    ) -> list[app.structures.base.PersonalPostDB]:
        posts: list[app.structures.base.PersonalPostDB] = cls.db.read(
            statement=cls.db.sqls.PersonalPosts.READ_USER_PERSONAL_POSTS,
            values=(tg_user_id,),
            connection=connection,
            fetch='fetchall',
        )
        return posts

    @classmethod
    def read(cls, post_id: int, connection: pg_ext_connection) -> app.structures.base.PersonalPostDB | None:
        post: app.structures.base.PersonalPostDB | None = cls.db.read(
            statement=cls.db.sqls.PersonalPosts.READ_PERSONAL_POST_BY_ID,
            values=(post_id,),
            connection=connection,
        )
        return post

    @classmethod
    def create(cls, author: int, message_id: int, connection: pg_ext_connection, ) -> int:
        """
        Sql is different with public post sample.
        """
        return cls.db.create(
            statement=cls.db.sqls.PersonalPosts.CREATE_PERSONAL_POST,
            values=(author, message_id),
            connection=connection,
        )

    @classmethod
    def delete(cls, post_id: int, connection: pg_ext_connection) -> None:
        return cls.db.delete(
            statement=cls.db.sqls.PersonalPosts.DELETE_PERSONAL_POST,
            values=(post_id,),
            connection=connection,
        )

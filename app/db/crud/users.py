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

from app.db import manager as db_manager

if TYPE_CHECKING:
    from psycopg2.extensions import connection as pg_ext_connection
    import app.structures.base


class User:
    db = db_manager.Postgres

    @classmethod
    def create(
            cls,
            tg_user_id: int,
            fullname: str,
            goal: app.structures.base.Goal,
            gender: app.structures.base.Gender,
            age: int,
            country: str,
            city: str,
            comment: str,
            connection: pg_ext_connection,
    ) -> None:
        return cls.db.create(
            connection=connection,
            statement=cls.db.sqls.Users.CREATE_USER,
            values=(tg_user_id, fullname, goal, gender, age, country, city, comment),
        )

    @classmethod
    def read(cls, tg_user_id: int, connection: pg_ext_connection, ) -> app.structures.base.ProfileDB | None:
        user_row: app.structures.base.ProfileDB = cls.db.read(
            statement=cls.db.sqls.Users.READ_USER,
            values=(tg_user_id,),
            connection=connection,
        )
        return user_row

    @classmethod
    def upsert(
            cls,
            tg_user_id: int,
            fullname: str,
            goal: app.structures.base.Goal,
            gender: app.structures.base.Gender,
            age: int,
            country: str,
            city: str,
            comment: str,
            connection: pg_ext_connection,
    ) -> None:
        return cls.db.create(
            statement=cls.db.sqls.Users.UPSERT_USER,
            values=(tg_user_id, fullname, goal, gender, age, country, city, comment) * 2,  # Multiply for upsert
            connection=connection
        )

    @classmethod
    def delete(cls, tg_user_id: int, connection: pg_ext_connection, ) -> None:  # Not in use
        return cls.db.delete(
            statement=cls.db.sqls.Users.DELETE_USER,
            values=(tg_user_id,),
            connection=connection,
        )


class Match:
    db = db_manager.Postgres

    @classmethod
    def create(cls, tg_user_id: int, matched_tg_user_id: int, connection: pg_ext_connection, ) -> None:
        return cls.db.create(
            statement=cls.db.sqls.ShownUsers.CREATE_SHOWN_USER,
            values=(tg_user_id, matched_tg_user_id),
            connection=connection,
        )


class Matcher:
    db = db_manager.Postgres

    @classmethod
    def drop_votes_table(cls, connection: pg_ext_connection, ) -> None:
        """Drop a table (user_votes) if you need completely new search (reselect user votes"""
        return cls.db.execute(
            statement=cls.db.sqls.Matches.Public.DROP_TEMP_TABLE_USER_VOTES,
            connection=connection,
        )

    @classmethod
    def drop_matches_table(cls, connection: pg_ext_connection, ) -> None:
        """Drop a table (user_covotes) if you need make search with new filters"""
        return cls.db.execute(
            statement=cls.db.sqls.Matches.Public.DROP_TEMP_TABLE_USER_COVOTES,
            connection=connection,
        )

    @classmethod
    def create_user_votes(cls, tg_user_id: int, connection: pg_ext_connection, ) -> None:
        """Caching, collect user votes in temporary table to increase performance"""
        cls.db.create(  # Create tmp table is create or execute? :)
            statement=cls.db.sqls.Matches.Public.CREATE_TEMP_TABLE_USER_VOTES,
            values=(tg_user_id,),
            connection=connection,
        )

    @classmethod
    def create_user_covotes(cls, tg_user_id: int, connection: pg_ext_connection, ) -> None:
        """Create and fill"""
        # Will be executed only if table not exists
        cls.db.create(
            statement=cls.db.sqls.Matches.Public.CREATE_TEMP_TABLE_USER_COVOTES,
            connection=connection,
        )
        cls.db.create(
            statement=cls.db.sqls.Matches.Public.FILL_TEMP_TABLE_USER_COVOTES,
            values=(tg_user_id,),
            connection=connection,
        )

    @classmethod
    def read_user_votes_count(cls, connection: pg_ext_connection, ) -> int:
        return cls.db.read(
            statement=cls.db.sqls.Matches.Public.READ_USER_VOTES_COUNT,
            connection=connection,
        )

    @classmethod
    def read_user_covotes_count(cls, connection: pg_ext_connection, ) -> int:
        return cls.db.read(
            statement=cls.db.sqls.Matches.Public.READ_USER_COVOTES_COUNT,
            connection=connection,
        )

    @classmethod
    def read_user_votes(cls, connection: pg_ext_connection, ) -> list[app.structures.base.UserPublicVote]:
        """
        Will create a temporary table with user votes
        There an option to select only one vote for checking
            but most likely in next steps will need to select rest votes
        """
        # Will be executed only if table not exists
        result = cls.db.read(  # ID inside the connection
            statement=cls.db.sqls.Matches.Public.READ_USER_VOTES,
            connection=connection,
            fetch='fetchall',
        )
        return result

    @classmethod
    def read_user_covotes(
            cls,
            tg_user_id: int,
            connection: pg_ext_connection,
            new: bool = False,
    ) -> list[app.structures.base.Covote]:
        """Will create a temporary table with user covotes"""
        # Will be executed only if table not exists
        if new is True:
            return cls.db.read(
                statement=cls.db.sqls.Matches.Public.READ_NEW_MATCHES,
                values=(tg_user_id,),  # Need to select a user from shown_users
                connection=connection,
                fetch='fetchall',
            )
        else:
            return cls.db.read(
                statement=cls.db.sqls.Matches.Public.READ_ALL_MATCHES,
                connection=connection,
                fetch='fetchall',
            )

    @classmethod
    def apply_goal_filter(cls, goal: int, connection: pg_ext_connection, ):
        cls.db.execute(
            statement=cls.db.sqls.Matches.Public.USE_GOAL_FILTER,
            values=(goal,),
            connection=connection,
        )

    @classmethod
    def apply_gender_filter(cls, gender: int, connection: pg_ext_connection, ):
        cls.db.execute(
            statement=cls.db.sqls.Matches.Public.USE_GENDER_FILTER,
            values=(gender,),
            connection=connection,
        )

    @classmethod
    def apply_age_filter(cls, min_age: int, max_age: int, connection: pg_ext_connection, ):
        cls.db.execute(
            statement=cls.db.sqls.Matches.Public.USE_AGE_FILTER,
            values=(min_age, max_age),
            connection=connection,
        )

    @classmethod
    def apply_checkboxes_country_filter(cls, connection: pg_ext_connection, ):
        cls.db.execute(statement=cls.db.sqls.Matches.Public.USE_CHECKBOX_COUNTRY_FILTER, connection=connection, )

    @classmethod
    def apply_checkboxes_city_filter(cls, connection: pg_ext_connection, ):
        cls.db.execute(statement=cls.db.sqls.Matches.Public.USE_CHECKBOX_CITY_FILTER, connection=connection, )

    @classmethod
    def apply_checkboxes_photo_filter(cls, connection: pg_ext_connection, ):
        cls.db.execute(statement=cls.db.sqls.Matches.Public.USE_CHECKBOX_PHOTO_FILTER, connection=connection, )

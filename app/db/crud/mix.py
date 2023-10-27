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

# noinspection PyPep8Naming
import app.db.manager

if TYPE_CHECKING:
    from psycopg2.extensions import connection as pg_ext_connection
    import app.structures.base


class System:
    db = app.db.manager.Postgres

    @classmethod
    def read_bots_ids(cls, connection: pg_ext_connection, ) -> list[int]:
        bots_ids = cls.db.read(
            statement=cls.db.sqls.System.READ_BOTS_IDS,
            values=(app.constants.I_AM_BOT,),
            connection=connection,
            fetch='fetchall',
        )
        return bots_ids

    @classmethod
    def read_all_users_ids(cls, connection: pg_ext_connection, ) -> list[int]:
        result = cls.db.read(
            statement=cls.db.sqls.System.READ_ALL_USERS_IDS,
            connection=connection,
            fetch='fetchall',
        )
        return result


class MatchStats:
    db = app.db.manager.Postgres

    @classmethod
    def read_user_personal_votes_statistic(
            cls,
            tg_user_id: int,
            connection: pg_ext_connection,
    ) -> app.structures.base.PersonalVotesStatsDB:
        personal_votes_statistic: app.structures.base.PersonalVotesStatsDB = cls.db.read(
            statement=cls.db.sqls.Matches.Personal.READ_USER_PERSONAL_VOTES_STATISTIC,
            values=(tg_user_id,),  # A bit dirty arg usage
            connection=connection,
        )
        return personal_votes_statistic

    @classmethod
    def drop_temp_table_user_personal_votes(cls, connection: pg_ext_connection, ) -> None:
        cls.db.execute(
            statement=cls.db.sqls.Matches.Personal.DROP_TEMP_TABLE_USER_PERSONAL_VOTES,
            connection=connection,
        )

    @classmethod
    def create_temp_table_personal_votes(cls, tg_user_id: int, connection: pg_ext_connection, ) -> None:
        cls.db.execute(
            statement=cls.db.sqls.Matches.Personal.CREATE_TEMP_TABLE_PERSONAL_VOTES,
            values=(tg_user_id,),
            connection=connection,
        )  # Move to user class?

    @classmethod
    def read_personal_covotes_count(
            cls,
            tg_user_id: int,
            connection: pg_ext_connection,
    ) -> app.structures.base.PersonalVotesStatsDB:
        result = cls.db.read(
            statement=cls.db.sqls.Matches.Personal.READ_PERSONAL_COVOTES_COUNT,
            values=(tg_user_id,) * 3,
            connection=connection,
        )
        return result

    @classmethod
    def drop_temp_table_my_and_covote_personal_votes(cls, connection: pg_ext_connection, ) -> None:
        cls.db.execute(
            statement=cls.db.sqls.Matches.Personal.DROP_TEMP_TABLE_MY_AND_COVOTE_PERSONAL_VOTES,
            connection=connection,
        )

    @classmethod
    def create_temp_table_my_and_covote_personal_votes(
            cls,
            tg_user_id: int,
            with_tg_user_id: int,
            connection: pg_ext_connection,
    ) -> None:
        cls.db.execute(
            statement=cls.db.sqls.Matches.Personal.CREATE_TEMP_TABLE_MY_AND_COVOTE_PERSONAL_VOTES,
            values=(tg_user_id, with_tg_user_id, tg_user_id),
            connection=connection,
        )


class Photo:
    db = app.db.manager.Postgres
    sqls = app.db.manager.Postgres.sqls

    @classmethod
    def create(cls, tg_user_id: int, photo: str, connection: pg_ext_connection, ) -> None:
        result = cls.db.create(
            statement=cls.db.sqls.Photos.CREATE_PHOTO,
            values=(tg_user_id, photo),
            connection=connection,
        )
        return result

    @classmethod
    def read(cls, tg_user_id: int, connection: pg_ext_connection, ) -> list[str]:
        result = cls.db.read(
            statement=cls.db.sqls.Photos.READ_PHOTOS,
            values=(tg_user_id,),
            connection=connection,
            fetch='fetchall',
        )
        return result

    @classmethod
    def delete_user_photos(cls, tg_user_id: int, connection: pg_ext_connection, ) -> None:
        result = cls.db.delete(
            statement=cls.db.sqls.Photos.DELETE_USER_PHOTOS,
            values=(tg_user_id,),
            connection=connection,
        )
        return result

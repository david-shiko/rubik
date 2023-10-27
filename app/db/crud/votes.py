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
    from app.models.users import User
    from app.models.votes import VoteBase
    import app.structures.base


class PublicVote:
    db = app.db.manager.Postgres

    @classmethod
    def create(  # not in use
            cls,
            tg_user_id: int,
            post_id: int,
            message_id: int,
            value: int | None,
            connection: pg_ext_connection,
    ) -> None:
        cls.db.create(
            statement=cls.db.sqls.PublicVotes.CREATE_PUBLIC_VOTE,
            values=(tg_user_id, post_id, message_id, value,),
            connection=connection,
        )

    @classmethod
    def read(
            cls,
            post_id: int,
            tg_user_id: int,
            connection: pg_ext_connection,
    ) -> app.structures.base.PublicVoteDB | None:
        vote_row: app.structures.base.PublicVoteDB = cls.db.read(
            statement=cls.db.sqls.PublicVotes.READ_PUBLIC_VOTE,
            values=(tg_user_id, post_id),
            connection=connection or connection,
        )
        if vote_row:
            vote_row['value'] = vote_row['value'] or 0  # Convert None to 0
            return vote_row

    @classmethod
    def update(cls, tg_user_id: int, post_id: int, value: int, connection: pg_ext_connection, ) -> None:
        return cls.db.update(
            statement=cls.db.sqls.PublicVotes.UPDATE_PUBLIC_VOTE_VALUE,
            connection=connection,
            values=(value, tg_user_id, post_id),
        )

    @classmethod
    def upsert_value(
            cls,
            tg_user_id: int,
            post_id: int,
            message_id: int,
            value: int,
            connection: pg_ext_connection,
    ) -> None:
        return cls.db.update(
            statement=cls.db.sqls.PublicVotes.UPSERT_PUBLIC_VOTE_VALUE,
            values=(tg_user_id, post_id, message_id, value, value,),  # "value" twice for upsert
            connection=connection,
        )

    @classmethod
    def upsert(  # Not in use
            cls,
            tg_user_id: int,
            post_id: int,
            message_id: int,
            connection: pg_ext_connection,
            value: VoteBase.Value = None,
    ) -> None:
        return cls.db.upsert(
            statement=cls.db.sqls.PublicVotes.UPSERT_PUBLIC_VOTE_VALUE,
            values=(tg_user_id, post_id, message_id, value),
            connection=connection,
        )

    @classmethod
    def upsert_message_id(
            cls,
            tg_user_id: int,
            post_id: int,
            new_message_id: int,
            connection: pg_ext_connection,
    ) -> None:
        return cls.db.execute(
            statement=cls.db.sqls.PublicVotes.UPSERT_PUBLIC_VOTE_MESSAGE_ID,
            values=(tg_user_id, post_id, new_message_id, new_message_id),
            connection=connection,
        )

    @classmethod
    def read_user_votes(
            cls,
            tg_user_id: int,
            connection: pg_ext_connection,
    ) -> list[app.structures.base.PublicVoteDB]:
        """
        Returns all (included non-votable (Zero or None)) votes from common table..
        To read only votable cached votes - use Matcher.get_user_votes (preferred).
        """
        vote_rows: list[app.structures.base.PublicVoteDB] = cls.db.read(
            statement=cls.db.sqls.PublicVotes.READ_USER_PUBLIC_VOTES,
            connection=connection,
            values=(tg_user_id,),
            fetch='fetchall',
        )
        return vote_rows

    @classmethod
    def read_user_votes_count(cls, tg_user_id: int, connection: pg_ext_connection) -> int:
        return cls.db.read(
            statement=cls.db.sqls.PublicVotes.READ_USER_PUBLIC_VOTES_COUNT,
            values=(tg_user_id,),
            connection=connection,
        )


class PersonalVote:
    db = app.db.manager.Postgres

    @classmethod
    def read(
            cls,
            tg_user_id: int,
            connection: pg_ext_connection,
            post_id: int,
    ) -> app.structures.base.PersonalVoteDB | None:
        vote_row: app.structures.base.PersonalVoteDB = cls.db.read(
            statement=cls.db.sqls.PersonalVotes.READ_PERSONAL_VOTE,
            values=(tg_user_id, post_id),
            connection=connection,
        )
        if vote_row:
            vote_row['value'] = vote_row['value'] or 0  # Convert None to 0
            return vote_row
        return None

    @classmethod
    def upsert(
            cls,
            tg_user_id: int,
            post_id: int,
            message_id: int,
            value: int,
            connection: pg_ext_connection = ...,
    ) -> None:
        return cls.db.execute(
            statement=cls.db.sqls.PersonalVotes.UPSERT_PERSONAL_VOTE,
            values=(tg_user_id, post_id, message_id, value, message_id, value),
            connection=connection,
        )

    @classmethod
    def upsert_message_id(
            cls,
            tg_user_id: int,
            post_id: int,
            new_message_id: int,
            connection: pg_ext_connection,
    ) -> None:
        return cls.db.execute(
            statement=cls.db.sqls.PersonalVotes.UPSERT_PERSONAL_VOTE_MESSAGE_ID,
            values=(tg_user_id, post_id, new_message_id, new_message_id),
            connection=connection,
        )

    @classmethod
    def read_user_votes(
            cls,
            tg_user_id: int,
            connection: pg_ext_connection,
    ) -> list[app.structures.base.PersonalVoteDB]:
        """Returns all (included nonvotable (Zero or None)) votes from common table. Not in use currently."""
        vote_rows: list[app.structures.base.PersonalVoteDB] = cls.db.read(
            statement=cls.db.sqls.PersonalVotes.READ_USER_PERSONAL_VOTES,
            connection=connection,
            values=(tg_user_id,),
            fetch='fetchall'
        )
        return vote_rows

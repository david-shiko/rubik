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
from typing import TYPE_CHECKING, Any as typing_Any
from unittest.mock import patch

import pytest

import app.db.crud.votes

if TYPE_CHECKING:
    from unittest.mock import MagicMock


class TestPublicVote:

    cls_to_test = app.db.crud.votes.PublicVote

    @pytest.fixture(scope='function')  # Will patch during all the test
    def patched_db(self, ) -> MagicMock:
        with patch.object(self.cls_to_test, 'db', autospec=True, ) as mock_postgres_db:
            yield mock_postgres_db

    def test_upsert_message_id(self, patched_db: MagicMock, ):
        self.cls_to_test.upsert_message_id(
            tg_user_id=1,
            post_id=2,
            new_message_id=3,
            connection=typing_Any,
        )
        patched_db.execute.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.PublicVotes.UPSERT_PUBLIC_VOTE_MESSAGE_ID,
            values=(1, 2, 3, 3,),
            connection=typing_Any,
        )

    def test_read(self, patched_db: MagicMock, public_vote_db_s: app.structures.base.PublicVoteDB, ):
        patched_db.read.return_value = public_vote_db_s
        assert public_vote_db_s['value'] is None
        # Execution
        result = self.cls_to_test.read(
            post_id=public_vote_db_s['post_id'],
            tg_user_id=public_vote_db_s['tg_user_id'],
            connection=typing_Any,
        )
        # Checks
        patched_db.read.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.PublicVotes.READ_PUBLIC_VOTE,
            values=(public_vote_db_s['tg_user_id'], public_vote_db_s['post_id'],),
            connection=typing_Any,
        )
        assert len(patched_db.mock_calls) == 1
        assert result == public_vote_db_s
        assert result['value'] == 0

    def test_create(self, patched_db: MagicMock, ):
        self.cls_to_test.create(tg_user_id=1, post_id=2, message_id=3, value=4, connection=typing_Any, )
        patched_db.create.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.PublicVotes.CREATE_PUBLIC_VOTE,
            values=(1, 2, 3, 4),
            connection=typing_Any,
        )

    def test_read_user_votes(self, patched_db: MagicMock, public_vote_db_s: app.structures.base.PublicVoteDB, ):
        result = self.cls_to_test.read_user_votes(
            tg_user_id=public_vote_db_s['tg_user_id'],
            connection=typing_Any,
        )
        patched_db.read.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.PublicVotes.READ_USER_PUBLIC_VOTES,
            connection=typing_Any,
            values=(public_vote_db_s['tg_user_id'],),
            fetch='fetchall',
        )
        assert len(patched_db.mock_calls) == 1
        assert result == patched_db.read.return_value

    def test_update(self, patched_db: MagicMock, ):
        # TODO rename method to value
        self.cls_to_test.update(connection=typing_Any, tg_user_id=1, post_id=2, value=3, )
        patched_db.update.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.PublicVotes.UPDATE_PUBLIC_VOTE_VALUE,
            connection=typing_Any,
            values=(3, 1, 2),
        )

    def test_upsert(self, patched_db: MagicMock, ):
        self.cls_to_test.upsert(
            tg_user_id=1,
            post_id=2,
            message_id=3,
            connection=typing_Any,
            value=4,
        )
        patched_db.upsert.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.PublicVotes.UPSERT_PUBLIC_VOTE_VALUE,
            values=(1, 2, 3, 4),
            connection=typing_Any,
        )

    def test_upsert_value(self, patched_db: MagicMock, ):
        self.cls_to_test.upsert_value(
            tg_user_id=1,
            post_id=2,
            message_id=3,
            value=4,
            connection=typing_Any,
        )
        patched_db.update.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.PublicVotes.UPSERT_PUBLIC_VOTE_VALUE,
            values=(1, 2, 3, 4, 4,),  # "value" twice for upsert
            connection=typing_Any,
        )

    def test_read_user_votes_count(self, patched_db: MagicMock, user_s: app.models.users.User, ):
        assert self.cls_to_test.read_user_votes_count(
            tg_user_id=user_s.tg_user_id,
            connection=user_s.connection,
        )
        patched_db.read.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.PublicVotes.READ_USER_PUBLIC_VOTES_COUNT,
            values=(user_s.tg_user_id,),
            connection=user_s.connection,
        )


class TestPersonalVote:
    cls_to_test = app.db.crud.votes.PersonalVote

    @pytest.fixture(scope='function')  # Will patch during all the test
    def patched_db(self, ) -> MagicMock:
        with patch.object(self.cls_to_test, 'db', autospec=True, ) as mock_postgres_db:
            yield mock_postgres_db

    def test_upsert(self, patched_db: MagicMock, personal_vote_db_s: app.structures.base.PersonalVoteDB, ):
        self.cls_to_test.upsert(
            tg_user_id=personal_vote_db_s['tg_user_id'],
            post_id=personal_vote_db_s['post_id'],
            message_id=personal_vote_db_s['message_id'],
            value=personal_vote_db_s['value'],
            connection=typing_Any,
        )
        patched_db.execute.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.PersonalVotes.UPSERT_PERSONAL_VOTE,
            # Two more args for upsert
            values=(*personal_vote_db_s.values(), personal_vote_db_s['message_id'], personal_vote_db_s['value'],),
            connection=typing_Any,
        )
        assert len(patched_db.mock_calls) == 1

    def test_upsert_message_id(self, patched_db: MagicMock, ):
        self.cls_to_test.upsert_message_id(
            tg_user_id=1,
            post_id=2,
            new_message_id=3,
            connection=typing_Any,
        )
        patched_db.execute.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.PersonalVotes.UPSERT_PERSONAL_VOTE_MESSAGE_ID,
            values=(1, 2, 3, 3,),
            connection=typing_Any,
        )

    def test_read(self, patched_db: MagicMock, personal_vote_db_s: app.structures.base.PersonalVoteDB, ):
        patched_db.read.return_value = personal_vote_db_s
        assert personal_vote_db_s['value'] is None
        # Execution
        result = self.cls_to_test.read(
            tg_user_id=personal_vote_db_s['tg_user_id'],
            post_id=personal_vote_db_s['post_id'],
            connection=typing_Any,
        )
        # Checks
        patched_db.read.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.PersonalVotes.READ_PERSONAL_VOTE,
            values=(personal_vote_db_s['tg_user_id'], personal_vote_db_s['post_id']),
            connection=typing_Any,
        )
        assert len(patched_db.mock_calls) == 1
        assert result == patched_db.read.return_value
        assert result['value'] == 0

    def test_read_user_votes(self, patched_db: MagicMock, ):
        result = self.cls_to_test.read_user_votes(tg_user_id=1, connection=typing_Any, )
        # Checks
        patched_db.read.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.PersonalVotes.READ_USER_PERSONAL_VOTES,
            values=(1,),
            connection=typing_Any,
            fetch='fetchall',
        )
        assert result == patched_db.read.return_value

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
from unittest.mock import patch, call

import pytest

import app.db.crud.users

if TYPE_CHECKING:
    from unittest.mock import MagicMock


class TestMatcher:

    cls_to_test = app.db.crud.users.Matcher

    @pytest.fixture(scope='function')  # Will patch during all the test
    def patched_db(self, ) -> MagicMock:
        with patch.object(self.cls_to_test, 'db', autospec=True, ) as mock_db:
            yield mock_db

    def test_drop_votes_table(self, patched_db: MagicMock, ):
        self.cls_to_test.drop_votes_table(connection=typing_Any, )
        patched_db.execute.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.Matches.Public.DROP_TEMP_TABLE_USER_VOTES,
            connection=typing_Any,
        )
        assert len(patched_db.mock_calls) == 1

    def test_drop_matches_table(self, patched_db: MagicMock, ):
        self.cls_to_test.drop_matches_table(connection=typing_Any, )
        patched_db.execute.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.Matches.Public.DROP_TEMP_TABLE_USER_COVOTES,
            connection=typing_Any,
        )
        assert len(patched_db.mock_calls) == 1

    def test_create_user_votes(self, patched_db: MagicMock, ):
        """Caching, collect user votes in temporary table to increase performance"""
        self.cls_to_test.create_user_votes(tg_user_id=1, connection=typing_Any, )
        patched_db.create.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.Matches.Public.CREATE_TEMP_TABLE_USER_VOTES,
            values=(1,),
            connection=typing_Any,
        )

    def test_create_user_covotes(self, patched_db: MagicMock, ):
        """Caching, collect user covotes in temporary table to increase performance"""
        self.cls_to_test.create_user_covotes(tg_user_id=1, connection=typing_Any, )
        assert patched_db.create.call_args_list == [call(
            statement=self.cls_to_test.db.sqls.Matches.Public.CREATE_TEMP_TABLE_USER_COVOTES,
            connection=typing_Any,
        ),
            call(
                statement=self.cls_to_test.db.sqls.Matches.Public.FILL_TEMP_TABLE_USER_COVOTES,
                values=(1,),
                connection=typing_Any,
            ),
        ]

    def test_read_user_votes(self, patched_db: MagicMock, ):
        result = self.cls_to_test.read_user_votes(connection=typing_Any, )
        # Checks
        patched_db.read.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.Matches.Public.READ_USER_VOTES,
            connection=typing_Any,
            fetch='fetchall',
        )
        assert result == patched_db.read.return_value

    def test_read_user_votes_count(self, patched_db: MagicMock, ):
        result = self.cls_to_test.read_user_votes_count(connection=typing_Any, )
        # Checks
        patched_db.read.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.Matches.Public.READ_USER_VOTES_COUNT,
            connection=typing_Any,
        )
        assert result == patched_db.read.return_value

    def test_read_user_covotes_count(self, patched_db: MagicMock, ):
        result = self.cls_to_test.read_user_covotes_count(connection=typing_Any, )
        # Checks
        patched_db.read.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.Matches.Public.READ_USER_COVOTES_COUNT,
            connection=typing_Any,
        )
        assert result == patched_db.read.return_value

    def test_read_user_covotes_all(self, patched_db: MagicMock, ):
        result = self.cls_to_test.read_user_covotes(tg_user_id=1, connection=typing_Any, new=False, )
        # Checks
        patched_db.read.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.Matches.Public.READ_ALL_MATCHES,
            connection=typing_Any,
            fetch='fetchall',
        )
        assert result == patched_db.read.return_value

    def test_read_user_covotes_new(self, patched_db: MagicMock, ):
        result = self.cls_to_test.read_user_covotes(tg_user_id=1, connection=typing_Any, new=True, )
        # Checks
        patched_db.read.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.Matches.Public.READ_NEW_MATCHES,
            connection=typing_Any,
            values=(1,),
            fetch='fetchall',
        )
        assert result == patched_db.read.return_value

    def test_apply_goal_filter(self, patched_db: MagicMock, ):
        self.cls_to_test.apply_goal_filter(goal=1, connection=typing_Any, )
        patched_db.execute.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.Matches.Public.USE_GOAL_FILTER,
            values=(1,),
            connection=typing_Any,
        )

    def test_apply_gender_filter(self, patched_db: MagicMock, ):
        self.cls_to_test.apply_gender_filter(gender=1, connection=typing_Any, )
        patched_db.execute.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.Matches.Public.USE_GENDER_FILTER,
            values=(1,),
            connection=typing_Any,
        )

    def test_apply_age_filter(self, patched_db: MagicMock, ):
        self.cls_to_test.apply_age_filter(min_age=20, max_age=50, connection=typing_Any, )
        patched_db.execute.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.Matches.Public.USE_AGE_FILTER,
            values=(20, 50),
            connection=typing_Any,
        )

    def test_apply_checkboxes_country_filter(self, patched_db: MagicMock, ):
        self.cls_to_test.apply_checkboxes_country_filter(connection=typing_Any, )
        patched_db.execute.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.Matches.Public.USE_CHECKBOX_COUNTRY_FILTER,
            connection=typing_Any,
        )

    def test_apply_checkboxes_city_filter(self, patched_db: MagicMock, ):
        self.cls_to_test.apply_checkboxes_city_filter(connection=typing_Any, )
        patched_db.execute.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.Matches.Public.USE_CHECKBOX_CITY_FILTER,
            connection=typing_Any,
        )

    def test_apply_checkboxes_photo_filter(self, patched_db: MagicMock, ):
        self.cls_to_test.apply_checkboxes_photo_filter(connection=typing_Any, )
        patched_db.execute.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.Matches.Public.USE_CHECKBOX_PHOTO_FILTER,
            connection=typing_Any,
        )


class TestMatch:
    cls_to_test = app.db.crud.users.Match

    def test_create(self, match_s: app.models.matches.Match, ):
        with patch.object(self.cls_to_test.db, 'create', autospec=True, ) as mock_create:
            self.cls_to_test.create(
                tg_user_id=match_s.owner.tg_user_id,
                matched_tg_user_id=match_s.user.tg_user_id,
                connection=match_s.owner.connection,
            )
        mock_create.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.ShownUsers.CREATE_SHOWN_USER,
            values=(match_s.owner.tg_user_id, match_s.user.tg_user_id),  # Same user is ok
            connection=match_s.owner.connection,
        )
        assert len(mock_create.mock_calls) == 1

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

import app.db.crud.mix

if TYPE_CHECKING:
    from unittest.mock import MagicMock


class TestMatchStats:

    @staticmethod
    @pytest.fixture(scope='function')  # Will patch during all the test
    def patched_db() -> MagicMock:
        with patch.object(app.db.crud.mix.MatchStats, 'db', autospec=True, ) as mock_postgres_db:
            yield mock_postgres_db

    @staticmethod
    def test_drop_temp_table_user_personal_votes(patched_db: MagicMock, ):
        app.db.crud.mix.MatchStats.drop_temp_table_user_personal_votes(connection=typing_Any, )
        patched_db.execute.assert_called_once_with(
            statement=app.db.crud.mix.MatchStats.db.sqls.Matches.Personal.DROP_TEMP_TABLE_USER_PERSONAL_VOTES,
            connection=typing_Any,
        )

    @staticmethod
    def test_create_temp_table_personal_votes(patched_db: MagicMock, ):
        app.db.crud.mix.MatchStats.create_temp_table_personal_votes(tg_user_id=1, connection=typing_Any, )
        patched_db.execute.assert_called_once_with(
            statement=app.db.crud.mix.MatchStats.db.sqls.Matches.Personal.CREATE_TEMP_TABLE_PERSONAL_VOTES,
            values=(1,),
            connection=typing_Any,
        )

    @staticmethod
    def test_read_user_personal_votes_statistic(patched_db: MagicMock, ):
        result = app.db.crud.mix.MatchStats.read_user_personal_votes_statistic(
            tg_user_id=1,
            connection=typing_Any,
        )
        patched_db.read.assert_called_once_with(
            statement=app.db.crud.mix.MatchStats.db.sqls.Matches.Personal.READ_USER_PERSONAL_VOTES_STATISTIC,
            values=(1,),
            connection=typing_Any,
        )
        assert result == patched_db.read.return_value

    @staticmethod
    def test_read_personal_covotes_count(patched_db: MagicMock, ):
        app.db.crud.mix.MatchStats.read_personal_covotes_count(tg_user_id=1, connection=typing_Any, )
        patched_db.read.assert_called_once_with(
            statement=app.db.crud.mix.MatchStats.db.sqls.Matches.Personal.READ_PERSONAL_COVOTES_COUNT,
            values=(1,) * 3,
            connection=typing_Any,
        )

    @staticmethod
    def test_drop_temp_table_my_and_covote_personal_votes(patched_db: MagicMock, ):
        app.db.crud.mix.MatchStats.drop_temp_table_my_and_covote_personal_votes(connection=typing_Any, )
        patched_db.execute.assert_called_once_with(
            statement=app.db.crud.mix.MatchStats.db.sqls.Matches.Personal.DROP_TEMP_TABLE_MY_AND_COVOTE_PERSONAL_VOTES,
            connection=typing_Any,
        )

    @staticmethod
    def test_create_temp_table_my_and_covote_personal_votes(patched_db: MagicMock, ):
        app.db.crud.mix.MatchStats.create_temp_table_my_and_covote_personal_votes(
            tg_user_id=1,
            with_tg_user_id=2,
            connection=typing_Any,
        )
        patched_db.execute.assert_called_once_with(
            statement=app.db.crud.mix.MatchStats.db.sqls.Matches.Personal.CREATE_TEMP_TABLE_MY_AND_COVOTE_PERSONAL_VOTES,
            values=(1, 2, 1),
            connection=typing_Any,
        )


class TestSystem:

    @staticmethod
    @pytest.fixture(scope='function')  # Will patch during all the test
    def patched_db() -> MagicMock:
        with patch.object(app.db.crud.mix.System, 'db', autospec=True, ) as mock_postgres_db:
            yield mock_postgres_db

    @staticmethod
    def test_read_bots_ids(patched_db: MagicMock, ):
        result = app.db.crud.mix.System.read_bots_ids(connection=typing_Any, )
        patched_db.read.assert_called_once_with(
            statement=app.db.crud.mix.System.db.sqls.System.READ_BOTS_IDS,
            values=(app.constants.I_AM_BOT,),
            connection=typing_Any,
            fetch='fetchall',
        )
        assert result == patched_db.read.return_value

    @staticmethod
    def test_read_all_users_ids(patched_db: MagicMock, ):
        result = app.db.crud.mix.System.read_all_users_ids(connection=typing_Any, )
        patched_db.read.assert_called_once_with(
            statement=app.db.crud.mix.System.db.sqls.System.READ_ALL_USERS_IDS,
            connection=typing_Any,
            fetch='fetchall',
        )
        assert result == patched_db.read.return_value


class TestPhoto:
    @staticmethod
    @pytest.fixture(scope='function')  # Will patch during all the test
    def patched_db() -> MagicMock:
        with patch.object(app.db.crud.mix.Photo, 'db', autospec=True, ) as mock_postgres_db:
            yield mock_postgres_db

    @staticmethod
    def test_create(patched_db: MagicMock):
        app.db.crud.mix.Photo.create(tg_user_id=1, photo='foo', connection=typing_Any, )
        patched_db.create.assert_called_once_with(
            statement=app.db.crud.mix.Photo.db.sqls.Photos.CREATE_PHOTO,
            values=(1, 'foo'),
            connection=typing_Any,
        )
        assert len(patched_db.mock_calls) == 1

    @staticmethod
    def test_read(patched_db: MagicMock):
        result = app.db.crud.mix.Photo.read(tg_user_id=1, connection=typing_Any, )
        patched_db.read.assert_called_once_with(
            statement=app.db.crud.mix.Photo.db.sqls.Photos.READ_PHOTOS,
            values=(1,),
            connection=typing_Any,
            fetch='fetchall',
        )
        assert len(patched_db.mock_calls) == 1
        assert result == patched_db.read.return_value

    @staticmethod
    def test_delete_user_photos(patched_db: MagicMock):
        app.db.crud.mix.Photo.delete_user_photos(tg_user_id=1, connection=typing_Any, )
        patched_db.delete.assert_called_once_with(
            statement=app.db.crud.mix.Photo.db.sqls.Photos.DELETE_USER_PHOTOS,
            values=(1,),
            connection=typing_Any,
        )
        assert len(patched_db.mock_calls) == 1

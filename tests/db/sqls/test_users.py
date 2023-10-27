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
from datetime import datetime
from dateutil.relativedelta import relativedelta

from app.db import postgres_sqls

from .conftest import create_user, read_user, create_photo, create_shown_user, read_shown_user

if TYPE_CHECKING:
    from psycopg import Cursor


class TestUsers:
    """
    Probably bug with psycopg3. Instead of setting birthdate to current year - value,
    it's setting birthdate to current year - index of value (5 in that case)
    See: https://github.com/psycopg/psycopg/issues/594#issue-1792154366
    """
    # See docstring about -5 year
    default_expected = {
        'tg_user_id': 1,
        'fullname': 'Test User',
        'goal': 1,
        'gender': 1,
        'birthdate': (datetime.now() - relativedelta(years=5)).date(),
        'country': None,
        'city': None,
        'comment': 'Hello, world!',
    }

    test_cls = postgres_sqls.Users

    def test_create_user(self, cursor: Cursor, ):
        assert read_user(user_id=1, cursor=cursor, ) is None
        cursor.execute(self.test_cls.CREATE_USER, tuple(self.default_expected.values()))
        result = read_user(user_id=1, cursor=cursor, )
        assert result == self.default_expected

    def test_upsert_user(self, cursor: Cursor, ):
        create_user(cursor=cursor, )
        new_params = expected = self.default_expected | {'fullname': 'New Test User'}
        cursor.execute(self.test_cls.UPSERT_USER, tuple(new_params.values()) * 2)
        result = read_user(user_id=1, cursor=cursor, )
        result['birthdate'] = expected['birthdate']  # Just quickfix, some troubles with date in beta psycopg3
        assert result == expected

    def test_is_registered(self, cursor: Cursor, ):
        create_user(cursor=cursor, )
        cursor.execute(self.test_cls.IS_REGISTERED, (1,))
        result = cursor.fetchone()
        assert result is not None  # Just not None check cuz column not specified in the query

    def test_read_user(self, cursor: Cursor, ):
        create_user(cursor=cursor, )
        expected = self.default_expected | {'age': 5}  # See cls docstring
        del expected['tg_user_id']
        del expected['birthdate']
        cursor.execute(self.test_cls.READ_USER, (1,))
        result = cursor.fetchone()
        assert result == expected

    def test_delete_user(self, cursor: Cursor, ):
        create_user(cursor=cursor, )
        cursor.execute(self.test_cls.DELETE_USER, (1,))
        assert read_user(user_id=1, cursor=cursor, ) is None


class TestPhotos:

    test_cls = postgres_sqls.Photos
    photo = {"tg_user_id": 1, "tg_photo_file_id": "foo"}
    default_expected = {'tg_photo_file_id': photo['tg_photo_file_id'], }

    def test_create_photo(self, cursor, ):
        result = create_photo(cursor=cursor, )
        assert result == {'id': 1, }

    def test_read_photos(self, cursor, ):
        create_photo(cursor=cursor)
        cursor.execute(self.test_cls.READ_PHOTOS, (self.photo["tg_user_id"],))
        result = cursor.fetchall()
        assert result == [self.default_expected, ]

    def test_delete_photo(self, cursor, ):
        result = create_photo(cursor=cursor, )
        cursor.execute(self.test_cls.DELETE_PHOTO, (result['id'],))
        cursor.execute(self.test_cls.READ_PHOTOS, (self.photo["tg_user_id"],))
        result = cursor.fetchall()
        assert result == []

    def test_delete_user_photos(self, cursor, ):
        create_photo(cursor=cursor, user_id=1, )  # Should be deleted
        create_photo(cursor=cursor, user_id=2, )  # Should not be deleted
        cursor.execute(self.test_cls.DELETE_USER_PHOTOS, (1,))
        cursor.execute(self.test_cls.READ_PHOTOS, (1,))
        result = cursor.fetchall()
        assert result == []
        cursor.execute(self.test_cls.READ_PHOTOS, (2,))
        result = cursor.fetchall()
        assert result == [self.default_expected, ]


class TestShownUsers:

    test_cls = postgres_sqls.ShownUsers
    shown_user = {"tg_user_id": 1, "shown_id": 2}
    default_expected = {"shown_id": shown_user['shown_id']}

    def test_create_shown_user(self, cursor, ):
        create_shown_user(cursor=cursor, )
        result = read_shown_user(cursor=cursor, user_id=1, )
        assert result == self.default_expected

    def test_create_shown_user_already_exists(self, cursor, ):
        """
        Test that shown_time updated
        Explicit commit after first 'create' call because PostgreSQL's 'CURRENT_TIMESTAMP'
        function only gets evaluated once per transaction.
        """
        create_shown_user(cursor, user_id=1, shown_id=2, )
        first_result = read_shown_user(cursor=cursor, columns=('created_at',), )
        cursor.connection.commit()  # Try to use time_sleep(0.1) if timestamp the same
        create_shown_user(cursor, user_id=1, shown_id=2, )
        second_result = read_shown_user(cursor=cursor, columns=('created_at',), )
        assert second_result['created_at'] > first_result['created_at']


class TestSystem:

    test_cls = postgres_sqls.System

    def test_read_bots_ids(self, cursor, ):
        create_user(cursor, user_id=1, comment='1', )
        create_user(cursor, user_id=2, comment='bot', )
        cursor.execute(self.test_cls.READ_BOTS_IDS, ("bot",))
        result = cursor.fetchall()
        assert result == [{'tg_user_id': 2}, ]

    def test_read_all_users_ids(self, cursor, ):
        create_user(cursor, user_id=1, comment='1', )
        create_user(cursor, user_id=2, comment='2', )
        cursor.execute(self.test_cls.READ_ALL_USERS_IDS)
        result = cursor.fetchall()
        assert result == [{'tg_user_id': 1}, {'tg_user_id': 2}, ]

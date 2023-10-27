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

from app.db import postgres_sqls

from .conftest import create_user, create_public_post, create_personal_post, create_public_vote, create_personal_vote

if TYPE_CHECKING:
    from psycopg import Cursor


class TestPublicVotes:
    class SharedAttrs:
        test_cls = postgres_sqls.PublicVotes
        default_expected = {'tg_user_id': 1, 'post_id': 1, 'message_id': 2, 'value': 1}

    test_cls = SharedAttrs.test_cls
    default_expected = SharedAttrs.default_expected

    def test_create_public_vote(self, cursor: Cursor, ):
        create_public_post(cursor=cursor, )
        cursor.execute(self.test_cls.READ_PUBLIC_VOTE, (1, 1))
        before = cursor.fetchone()
        assert before != self.default_expected
        params = {'tg_user_id': 1, 'post_id': 1, 'message_id': 2, 'value': 1}
        cursor.execute(self.test_cls.CREATE_PUBLIC_VOTE, tuple(params.values()))
        cursor.execute(self.test_cls.READ_PUBLIC_VOTE, (1, 1))
        result = cursor.fetchone()
        assert result == self.default_expected

    def test_read_user_public_votes(self, cursor: Cursor, ):
        create_public_vote(cursor=cursor, )
        cursor.execute(self.test_cls.READ_USER_PUBLIC_VOTES, (1,))
        result = cursor.fetchall()
        assert result == [self.default_expected, ]

    def test_read_users_ids_voted_for_public_post(self, cursor: Cursor, ):
        create_public_vote(cursor=cursor, )
        cursor.execute(self.test_cls.READ_USERS_IDS_VOTED_FOR_PUBLIC_POST, (1,))
        result = cursor.fetchall()
        assert result == [{'tg_user_id': self.default_expected['tg_user_id']}, ]

    def test_read_user_public_votes_count(self, cursor: Cursor, ):
        create_public_vote(cursor=cursor, )
        create_user(cursor=cursor, )
        cursor.execute(self.test_cls.READ_USER_PUBLIC_VOTES_COUNT, (1,))
        result = cursor.fetchone()
        assert result['count'] == 1

    class TestUpsertPublicVoteValue(SharedAttrs):

        def test_create(self, cursor: Cursor, ):  # Not in use
            """Test create part of query"""
            create_public_post(cursor=cursor, )
            expected = params = {'tg_user_id': 1, 'post_id': 1, 'message_id': 2, 'value': 2, }
            cursor.execute(self.test_cls.UPSERT_PUBLIC_VOTE_VALUE, (*params.values(), params['value'],))
            cursor.execute(self.test_cls.READ_PUBLIC_VOTE, (1, 1))
            result = cursor.fetchone()
            assert result == expected

        def test_upsert(self, cursor: Cursor, ):
            """Test upsert part of query"""
            create_public_vote(cursor=cursor, )
            expected = params = {'tg_user_id': 1, 'post_id': 1, 'message_id': 2, 'value': 2, }
            cursor.execute(self.test_cls.UPSERT_PUBLIC_VOTE_VALUE, (*params.values(), params['value'],))
            cursor.execute(self.test_cls.READ_PUBLIC_VOTE, (1, 1))
            result = cursor.fetchone()
            assert result == expected

    def test_update_public_vote_value(self, cursor: Cursor, ):
        create_public_vote(cursor=cursor, )
        expected = {'tg_user_id': 1, 'post_id': 1, 'message_id': 2, 'value': 3}
        cursor.execute(self.test_cls.UPDATE_PUBLIC_VOTE_VALUE, (expected['value'], 1, 1))
        cursor.execute(self.test_cls.READ_PUBLIC_VOTE, (1, 1))
        result = cursor.fetchone()
        assert result == expected

    class TestUpsertPublicVoteMessageId(SharedAttrs):
        def test_create(self, cursor: Cursor, ):
            create_public_post(cursor=cursor, )
            params = {'tg_user_id': 1, 'post_id': 1, 'message_id': 3, }
            expected = params | {'value': None, }
            cursor.execute(self.test_cls.UPSERT_PUBLIC_VOTE_MESSAGE_ID, (*params.values(), params['message_id']))
            cursor.execute(self.test_cls.READ_PUBLIC_VOTE, (1, 1))
            result = cursor.fetchone()
            assert result == expected

        def test_upsert(self, cursor: Cursor, ):
            create_public_vote(cursor=cursor, value=None, )
            params = {'tg_user_id': 1, 'post_id': 1, 'message_id': 3, }
            expected = params | {'value': None, }
            cursor.execute(self.test_cls.UPSERT_PUBLIC_VOTE_MESSAGE_ID, (*params.values(), params['message_id']))
            cursor.execute(self.test_cls.READ_PUBLIC_VOTE, (1, 1))
            result = cursor.fetchone()
            assert result == expected

    def test_delete_public_vote(self, cursor: Cursor, ):
        cursor.execute(self.test_cls.DELETE_PUBLIC_VOTE, (1, 1))
        cursor.execute(self.test_cls.READ_PUBLIC_VOTE, (1, 1))
        result = cursor.fetchone()
        assert result is None


class TestPersonalVotes:

    class Shared:
        test_cls = postgres_sqls.PersonalVotes
        default_expected = {'tg_user_id': 1, 'post_id': 1, 'message_id': 2, 'value': 1}

        def read(self, cursor: Cursor, user_id: int = 1, post_id: int = 1, ) -> dict:
            cursor.execute(self.test_cls.READ_PERSONAL_VOTE, (user_id, post_id,))
            result = cursor.fetchone()
            return result

    test_cls = Shared.test_cls
    default_expected = Shared.default_expected
    read = Shared.read

    def test_create_personal_vote(self, cursor: Cursor, ):  # Not in use
        assert self.read(cursor=cursor, ) is None
        create_personal_vote(cursor=cursor, )
        assert self.read(cursor=cursor, ) == self.default_expected

    def test_read_user_personal_votes(self, cursor: Cursor, ):
        expected = [self.default_expected, self.default_expected | {'post_id': 2, }]
        create_personal_vote(cursor=cursor, user_id=1, post_id=1, )
        create_personal_vote(cursor=cursor, user_id=1, post_id=2, )
        cursor.execute(self.test_cls.READ_USER_PERSONAL_VOTES, (1,))
        result = cursor.fetchall()
        assert result == expected

    class TestUpsertPersonalVote(Shared, ):
        def test_create(self, cursor: Cursor, ):
            assert self.read(cursor=cursor, ) is None
            create_user(cursor=cursor, )
            create_personal_post(cursor=cursor, )
            params = self.default_expected | {'value': 2}
            cursor.execute(
                self.test_cls.UPSERT_PERSONAL_VOTE, (*params.values(), params['message_id'], params['value'])
            )
            cursor.execute(self.test_cls.READ_PERSONAL_VOTE, (1, 1))
            result = cursor.fetchone()
            assert result == params

        def test_upsert(self, cursor: Cursor, ):
            assert self.read(cursor=cursor, ) is None
            create_personal_vote(cursor=cursor, )
            params = self.default_expected | {'value': 2}
            cursor.execute(
                self.test_cls.UPSERT_PERSONAL_VOTE, (*params.values(), params['message_id'], params['value'])
            )
            cursor.execute(self.test_cls.READ_PERSONAL_VOTE, (1, 1))
            result = cursor.fetchone()
            assert result == params

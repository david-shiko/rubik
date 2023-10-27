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

from pytest import fixture, mark

from app.db import postgres_sqls

from .conftest import create_public_post, create_personal_post

if TYPE_CHECKING:
    from psycopg import Cursor


class TestPostBase:
    test_cls = postgres_sqls.PostsBase
    default_expected = {'id': 1, 'author': 2, 'message_id': 3, }

    def create(self, cursor, ) -> dict[str, int]:
        cursor.execute(self.test_cls.CREATE_POST_BASE, (2, 3))
        result = cursor.fetchone()
        return result

    @staticmethod
    def read(cursor, ) -> list[dict]:
        cursor.execute("SELECT id, author, message_id FROM posts_base", )
        result = cursor.fetchall()
        return result

    def test_create(self, cursor: Cursor, ):
        assert self.read(cursor=cursor, ) == []
        self.create(cursor=cursor, )
        result = self.read(cursor=cursor, )
        assert result == [self.default_expected, ]


class TestPublicPosts:
    test_cls = postgres_sqls.PublicPosts
    default_expected = {'post_id': 1, 'message_id': 2, 'author': 3, 'likes_count': 0, 'dislikes_count': 0, 'status': 0}

    def test_create_public_post(self, cursor: Cursor, ):
        cursor.execute(self.test_cls.CREATE_PUBLIC_POST, (1, 2))
        cursor.execute("SELECT * FROM public_posts WHERE post_id = %s", (1,))
        result = cursor.fetchone()
        assert result is not None

    def test_read_public_posts_ids(self, cursor: Cursor, ):
        create_public_post(cursor=cursor, )
        cursor.execute(self.test_cls.READ_PUBLIC_POSTS_IDS, )
        result = cursor.fetchall()
        assert result == [{'post_id': 1, }, ]

    def test_read_public_post_pattern(self, cursor: Cursor, ):
        create_public_post(cursor=cursor, )
        cursor.execute(self.test_cls.READ_PUBLIC_POST_PATTERN)
        result = cursor.fetchone()
        assert result == self.default_expected

    def test_read_public_post_by_id(self, cursor: Cursor, ):
        create_public_post(cursor=cursor, )
        cursor.execute(self.test_cls.READ_PUBLIC_POST_BY_ID, (1,))
        result = cursor.fetchone()
        assert result == self.default_expected

    def test_read_exclusive_public_post(self, cursor: Cursor, ):
        create_public_post(cursor=cursor, )
        cursor.execute(self.test_cls.READ_EXCLUSIVE_PUBLIC_POST, (0, 2))
        result = cursor.fetchone()
        assert result == self.default_expected

    def test_read_public_posts_by_status(self, cursor: Cursor, ):
        create_public_post(cursor=cursor, )
        cursor.execute(self.test_cls.READ_PUBLIC_POSTS_BY_STATUS, (0,))  # status
        result = cursor.fetchall()
        assert result == [self.default_expected]

    def test_read_public_post_mass(self, cursor: Cursor, ):
        create_public_post(cursor=cursor, )
        cursor.execute(self.test_cls.READ_PUBLIC_POST_MASS, (0,))  # status
        result = cursor.fetchone()
        assert result == self.default_expected

    def test_update_public_post_votes_count(self, cursor: Cursor, ):
        create_public_post(cursor=cursor, )
        expected = self.default_expected | {'likes_count': 1, 'dislikes_count': 1, }
        cursor.execute(self.test_cls.READ_PUBLIC_POST_BY_ID, (1,))
        before = cursor.fetchone()
        assert before != expected
        cursor.execute(self.test_cls.UPDATE_PUBLIC_POST_VOTES_COUNT, (1, 1, 1))
        cursor.execute(self.test_cls.READ_PUBLIC_POST_BY_ID, (1,))
        actual = cursor.fetchone()
        assert actual == expected

    def test_update_public_post_status(self, cursor: Cursor, ):
        create_public_post(cursor=cursor, )
        expected = {'post_id': 1, 'likes_count': 0, 'dislikes_count': 0, 'status': 1, 'release_time': None}
        cursor.execute("SELECT * FROM public_posts WHERE post_id = %s", (1,))
        before = cursor.fetchone()
        assert before != expected
        cursor.execute(self.test_cls.UPDATE_PUBLIC_POST_STATUS, (1, 1))
        cursor.execute("SELECT * FROM public_posts WHERE post_id = %s", (1,))
        actual = cursor.fetchone()
        assert actual == expected

    def test_delete_public_post(self, cursor: Cursor, ):
        create_public_post(cursor=cursor, )
        expected = None
        cursor.execute("SELECT * FROM public_posts WHERE post_id = %s", (1,))
        before = cursor.fetchone()
        assert before != expected
        cursor.execute(self.test_cls.DELETE_PUBLIC_POST, (1,))
        cursor.execute("SELECT * FROM public_posts WHERE post_id = %s", (1,))
        actual = cursor.fetchone()
        assert actual is None


class TestPersonalPosts:
    test_cls = postgres_sqls.PersonalPosts
    default_expected = {'post_id': 1, 'message_id': 2, 'author': 3, }

    def test_create_personal_post(self, cursor: Cursor, ):
        cursor.execute(self.test_cls.READ_PERSONAL_POST_BY_ID, (1,))
        before = cursor.fetchone()
        assert before != self.default_expected
        params = {'author': 3, 'message_id': 2, }
        cursor.execute(self.test_cls.CREATE_PERSONAL_POST, tuple(params.values()))
        cursor.execute(self.test_cls.READ_PERSONAL_POST_BY_ID, (1,))
        result = cursor.fetchone()
        assert result == self.default_expected

    def test_read_personal_posts_pattern(self, cursor: Cursor, ):
        create_personal_post(cursor=cursor, )
        cursor.execute(self.test_cls.READ_PERSONAL_POSTS_PATTERN, )
        result = cursor.fetchone()
        assert result == self.default_expected

    def test_read_personal_post_by_id(self, cursor: Cursor, ):
        create_personal_post(cursor=cursor, )
        cursor.execute(self.test_cls.READ_PERSONAL_POST_BY_ID, (1,))
        result = cursor.fetchone()
        assert result == self.default_expected

    def test_read_user_personal_posts(self, cursor: Cursor, ):
        create_personal_post(cursor=cursor, )
        cursor.execute(self.test_cls.READ_USER_PERSONAL_POSTS, (3,))
        result = cursor.fetchall()
        assert result == [{'post_id': 1, 'message_id': 2}, ]

    def test_delete_personal_post(self, cursor: Cursor, ):
        create_personal_post(cursor=cursor, )
        cursor.execute(self.test_cls.DELETE_PERSONAL_POST, (1,))
        cursor.execute(self.test_cls.READ_PERSONAL_POST_BY_ID, (1,))
        result = cursor.fetchone()
        assert result is None


class TestCollections:
    test_cls = postgres_sqls.Collections
    default_expected = {'collection_id': 1, 'author': 3, 'name': 'CollectionName'}

    @fixture
    def create_collection(self, cursor: Cursor, ) -> dict:
        params = {'author': 3, 'name': 'CollectionName'}
        cursor.execute(self.test_cls.CREATE_COLLECTION, tuple(params.values()))
        result = cursor.fetchone()
        yield result

    def test_create_collection(self, cursor: Cursor, ):
        params = {'author': 3, 'name': 'CollectionName'}
        cursor.execute(self.test_cls.CREATE_COLLECTION, tuple(params.values()))
        cursor.execute(self.test_cls.READ_USER_COLLECTION_ID_BY_NAME, tuple(params.values()))
        result = cursor.fetchone()
        assert result == {'collection_id': 1}

    def test_create_m2m_collections_posts(self, cursor: Cursor, create_collection: dict, ):
        create_public_post(cursor=cursor, message_id=2, )
        create_personal_post(cursor=cursor, message_id=3, )
        cursor.execute(self.test_cls.CREATE_M2M_COLLECTIONS_POSTS, (1, 1))  # collection_id and post_id
        cursor.execute("SELECT id, collection_id, post_id FROM m2m_collections_posts WHERE id = %s", (1,))
        result = cursor.fetchone()
        assert result == {'id': 1, 'collection_id': 1, 'post_id': 1}

    def test_read_user_collection_id_by_name(self, cursor: Cursor, create_collection: dict):
        cursor.execute(
            self.test_cls.READ_USER_COLLECTION_ID_BY_NAME,
            (self.default_expected['author'], self.default_expected['name']),
        )
        result = cursor.fetchone()
        assert result == {'collection_id': 1}

    @mark.skip(
        reason='Query for psycopg v2 and v3 are differ. '
               'V3 requires brackets but able to handle a flat tuple.'
               'V2 not requires brackets but unable to handle a flat tuple.'
    )
    def test_read_collections_by_ids(self, cursor: Cursor, create_collection: dict):
        cursor.execute(self.test_cls.READ_COLLECTIONS_BY_IDS, (1,))
        result = cursor.fetchall()
        assert result == [self.default_expected, ]

    def test_read_user_collections(self, cursor: Cursor, create_collection: dict):
        cursor.execute(self.test_cls.READ_USER_COLLECTIONS, (self.default_expected['author'],))
        result = cursor.fetchall()
        assert result == [self.default_expected, ]

    def test_read_public_collection_posts(self, cursor: Cursor, create_collection: dict, ):
        create_public_post(cursor=cursor, message_id=2, )
        create_personal_post(cursor=cursor, message_id=3, )
        params = {'author': 3, 'name': 'CollectionName'}
        cursor.execute(self.test_cls.CREATE_COLLECTION, tuple(params.values()))
        cursor.execute(self.test_cls.CREATE_M2M_COLLECTIONS_POSTS, (1, 1))  # Assume a public post with id 1 exists
        cursor.execute(self.test_cls.READ_PUBLIC_COLLECTION_POSTS, (1,))
        result = cursor.fetchall()
        assert result == [TestPublicPosts.default_expected, ]

    def test_read_personal_collection_posts(self, cursor: Cursor, create_collection: dict, ):
        create_personal_post(cursor=cursor, )
        params = {'author': 3, 'name': 'CollectionName'}
        cursor.execute(self.test_cls.CREATE_COLLECTION, tuple(params.values()))
        cursor.execute(self.test_cls.CREATE_M2M_COLLECTIONS_POSTS, (1, 1))
        cursor.execute(self.test_cls.READ_PERSONAL_COLLECTION_POSTS, (1,))
        result = cursor.fetchall()
        assert result == [TestPersonalPosts.default_expected, ]

    def test_read_default_collections(self, cursor: Cursor, create_collection: dict):
        cursor.execute(
            self.test_cls.READ_DEFAULT_COLLECTIONS,
            (self.default_expected['author'], self.default_expected['name'][:1]),
        )
        result = cursor.fetchall()
        assert result == [self.default_expected, ]

    def test_read_default_collection_names(self, cursor: Cursor, create_collection: dict):
        cursor.execute(
            self.test_cls.READ_DEFAULT_COLLECTION_NAMES,
            (self.default_expected['author'], self.default_expected['name'][:1]),
        )
        result = cursor.fetchall()
        assert result == [{'name': self.default_expected['name']}]

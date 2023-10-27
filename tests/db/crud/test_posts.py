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

import app.db.crud.posts

if TYPE_CHECKING:
    from unittest.mock import MagicMock


class TestPublicPost:

    cls_to_test = app.db.crud.posts.PublicPost

    @pytest.fixture(scope='function')  # Function to reset mocks
    def patched_db(self, ) -> MagicMock:
        with patch.object(self.cls_to_test, 'db', autospec=True, ) as mock_postgres_db:
            yield mock_postgres_db

    def test_create(self, patched_db: MagicMock, ):
        result = app.db.crud.posts.PublicPost.create(author=1, message_id=2, connection=typing_Any, )
        patched_db.create.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.PublicPosts.CREATE_PUBLIC_POST,
            values=(1, 2,),
            connection=typing_Any,
        )
        assert result == patched_db.create.return_value

    def test_read(self, patched_db: MagicMock, ):
        result = app.db.crud.posts.PublicPost.read(post_id=1, connection=typing_Any, )
        patched_db.read.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.PublicPosts.READ_PUBLIC_POST_BY_ID,
            values=(1,),
            connection=typing_Any,
        )
        assert result == patched_db.read.return_value

    def test_read_exclusive(self, patched_db: MagicMock, ):
        result = app.db.crud.posts.PublicPost.read_exclusive(tg_user_id=1, status=2, connection=typing_Any, )
        patched_db.read.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.PublicPosts.READ_EXCLUSIVE_PUBLIC_POST,
            values=(2, 1,),
            connection=typing_Any,
        )
        assert result == patched_db.read.return_value

    def test_update_votes_count(self, patched_db: MagicMock, public_post_s: app.models.posts.PublicPost, ):
        app.db.crud.posts.PublicPost.update_votes_count(
            post_id=public_post_s.post_id,
            likes_count=public_post_s.likes_count,
            dislikes_count=public_post_s.dislikes_count,
            connection=public_post_s.author.connection,
        )
        patched_db.update.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.PublicPosts.UPDATE_PUBLIC_POST_VOTES_COUNT,
            values=(public_post_s.likes_count, public_post_s.dislikes_count, public_post_s.post_id,),
            connection=public_post_s.author.connection,
        )

    def test_read_voted_users_ids(self, patched_db: MagicMock, public_post_s: app.models.posts.PublicPost, ):
        result = app.db.crud.posts.PublicPost.read_voted_users_ids(
            post_id=public_post_s.post_id,
            connection=public_post_s.author.connection,
        )
        patched_db.read.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.PublicVotes.READ_USERS_IDS_VOTED_FOR_PUBLIC_POST,  # Votes sql
            values=(public_post_s.post_id,),
            connection=public_post_s.author.connection,
            fetch='fetchall',
        )
        assert result == patched_db.read.return_value

    def test_update_post_status(self, patched_db: MagicMock, public_post_s: app.models.posts.PublicPost, ):
        app.db.crud.posts.PublicPost.update_status(
            post_id=public_post_s.post_id,
            status=public_post_s.status,
            connection=public_post_s.author.connection,
        )
        patched_db.update.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.PublicPosts.UPDATE_PUBLIC_POST_STATUS,
            values=(public_post_s.status, public_post_s.post_id,),
            connection=public_post_s.author.connection,
        )

    @pytest.mark.parametrize(argnames='status', argvalues=app.models.posts.PublicPost.Status, )
    def test_read_pending_posts(self, patched_db: MagicMock, status: app.models.posts.PublicPost.Status):
        result = app.db.crud.posts.PublicPost.read_public_posts_by_status(connection=typing_Any, status=status, )
        patched_db.read.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.PublicPosts.READ_PUBLIC_POSTS_BY_STATUS,
            values=(status,),
            connection=typing_Any,
            fetch='fetchall',
        )
        assert result == patched_db.read.return_value

    @pytest.mark.parametrize(argnames='status', argvalues=app.models.posts.PublicPost.Status, )
    def test_read_mass(self, patched_db: MagicMock, status: app.models.posts.PublicPost.Status, ):
        result = app.db.crud.posts.PublicPost.read_mass(connection=typing_Any, status=status.value, )
        patched_db.read.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.PublicPosts.READ_PUBLIC_POST_MASS,
            values=(status,),
            connection=typing_Any,
        )
        assert result == patched_db.read.return_value


class TestPersonalPost:
    cls_to_test = app.db.crud.posts.PersonalPost

    @pytest.fixture(scope='function')
    def patched_db(self, ) -> MagicMock:
        with patch.object(self.cls_to_test, 'db', autospec=True, ) as mock_db:
            yield mock_db

    def test_create(self, patched_db: MagicMock, ):
        result = app.db.crud.posts.PersonalPost.create(author=1, message_id=2, connection=typing_Any, )
        patched_db.create.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.PersonalPosts.CREATE_PERSONAL_POST,
            values=(1, 2,),
            connection=typing_Any,
        )
        assert result == patched_db.create.return_value

    def test_read_user_posts(self, patched_db: MagicMock, personal_post_raw: app.structures.base.PersonalPostDB, ):
        result = app.db.crud.posts.PersonalPost.read_user_posts(
            tg_user_id=1,
            connection=typing_Any,
        )
        patched_db.read.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.PersonalPosts.READ_USER_PERSONAL_POSTS,
            values=(1,),
            connection=typing_Any,
            fetch='fetchall',
        )
        assert result == patched_db.read.return_value

    def test_read(self, patched_db: MagicMock, personal_post_raw: app.structures.base.PersonalPostDB, ):
        result = app.db.crud.posts.PersonalPost.read(
            post_id=personal_post_raw['post_id'],
            connection=typing_Any,
        )
        patched_db.read.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.PersonalPosts.READ_PERSONAL_POST_BY_ID,
            values=(personal_post_raw['post_id'],),
            connection=typing_Any,
        )
        assert result == patched_db.read.return_value

    def test_delete(self, patched_db: MagicMock, personal_post_raw: app.structures.base.PersonalPostDB, ):
        app.db.crud.posts.PersonalPost.delete(
            post_id=personal_post_raw['post_id'],
            connection=typing_Any,
        )
        patched_db.delete.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.PersonalPosts.DELETE_PERSONAL_POST,
            values=(personal_post_raw['post_id'],),
            connection=typing_Any,
        )

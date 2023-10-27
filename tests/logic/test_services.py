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
from unittest.mock import patch
from typing import TYPE_CHECKING, Any as typing_Any

import pytest

import app.models.collections
from app.services import System, Collection, PublicPost

if TYPE_CHECKING:
    from app.models.posts import (
        PublicPostInterface as PublicPostModelInterface,
        PersonalPostInterface as PersonalPostInterface,
    )
    from unittest.mock import MagicMock
    from faker import Faker


class TestCollection:

    @staticmethod
    @pytest.mark.parametrize(
        argnames='prefix', argvalues=[
            Collection.NamePrefix.PUBLIC.value,
            Collection.NamePrefix.PERSONAL.value
        ]
    )
    def test_get_defaults(user_s: app.models.users.User, prefix: str, ):
        with patch.object(
                Collection.Mapper.Model,
                'get_defaults',
                autospec=True,
        ) as mock_get_defaults:
            result = Collection.get_defaults(prefix=prefix, )
        # Checks
        mock_get_defaults.assert_called_once_with(
            prefix=prefix,
            author=Collection.user,
        )
        assert result == mock_get_defaults.return_value

    @staticmethod
    @pytest.mark.parametrize(argnames='prefix', argvalues=Collection.NamePrefix, )
    def test_get_defaults_names(prefix: Collection.NamePrefix, ):
        with patch.object(
                Collection.Mapper.Model,
                'get_defaults_names',
        ) as mock_get_defaults_names:
            result = Collection.get_defaults_names(prefix=prefix, )
            mock_get_defaults_names.assert_called_once_with(
                prefix=prefix.value,
                connection=Collection.user.connection,
            )
            expected = [Collection.remove_prefix(name=name, ) for name in mock_get_defaults_names.return_value]
            assert result == expected

    @staticmethod
    @pytest.mark.parametrize(argnames='prefix', argvalues=Collection.NamePrefix, )
    def test_create_default(
            prefix: Collection.NamePrefix,
            public_post_s: PublicPostModelInterface,
            personal_post_s: PersonalPostInterface,
    ):
        # Set up test inputs
        with patch.object(Collection.Mapper.Model, 'create', autospec=True, ) as mock_create:
            Collection.create_default(
                posts=[personal_post_s, personal_post_s],
                prefix=prefix,
                name='foo',
            )
        mock_create.assert_called_once_with(
            author=Collection.user,
            name=f'{prefix.value}_foo',
            posts_ids=[personal_post_s.post_id, personal_post_s.post_id],
        )

    @staticmethod
    @pytest.mark.parametrize(argnames='prefix', argvalues=Collection.NamePrefix, )
    def test_remove_prefix(prefix: Collection.NamePrefix, faker: Faker, ):
        result = Collection.remove_prefix(name=f'{prefix.value}_{faker.word()}', )
        assert prefix.value not in result

    @staticmethod
    def test_remove_prefixes(mock_collection: MagicMock, ):
        with patch.object(Collection, 'remove_prefix', autospec=True, ) as mock_remove_prefix:
            original_collection_name = mock_collection.name
            modified_collection_name = mock_remove_prefix.return_value
            Collection.remove_prefixes(collections=[mock_collection, ])
        mock_remove_prefix.assert_called_once_with(name=original_collection_name)
        assert mock_collection.name == modified_collection_name

    @staticmethod
    def test_get_by_ids():
        with (
            patch.object(Collection.Mapper.Model, 'get_by_ids', autospec=True, ) as mock_get_by_ids,
            patch.object(Collection, 'remove_prefixes', autospec=True, ) as mock_remove_prefix,
        ):
            result = Collection.get_by_ids(ids=[1, ], user=Collection.user, )
        mock_remove_prefix.assert_called_once_with(collections=mock_get_by_ids.return_value, )
        mock_get_by_ids.assert_called_once_with(ids=[1, ], user=Collection.user, )
        assert result == mock_get_by_ids.return_value


class TestSystem:

    @staticmethod
    @pytest.fixture(scope='function')
    def patched_crud() -> MagicMock:
        with patch.object(app.services.System, 'CRUD', autospec=True, ) as mock_crud:
            yield mock_crud

    @staticmethod
    def test_set_bot_votes(
            patched_crud: MagicMock,
            mock_public_post_f: MagicMock,
    ):
        patched_crud.read_bots_ids.return_value = [1]
        with (
            patch.object(app.services.System, 'Mapper', autospec=True, ) as mock_Mapper,
            patch.object(System.generator, 'gen_vote', autospec=True, ) as mock_gen_vote,
        ):
            System.set_bots_votes_to_post(post=mock_public_post_f, )
        # CHECKS
        mock_Mapper.User.assert_called_once_with(tg_user_id=1, connection=System.connection, )
        patched_crud.read_bots_ids.assert_called_once_with(connection=System.connection, )
        mock_gen_vote.assert_called_once_with(
            user=mock_Mapper.User.return_value,
            post=mock_public_post_f,
        )
        mock_Mapper.User.return_value.set_vote.assert_called_once_with(
            vote=mock_gen_vote.return_value,
            post=mock_public_post_f,
        )

    @staticmethod
    def test_read_bots_ids(patched_crud: MagicMock, ):
        result = System.read_bots_ids()
        patched_crud.read_bots_ids.assert_called_once_with(connection=System.connection, )
        assert result == patched_crud.read_bots_ids.return_value

    @staticmethod
    def test_read_all_users_ids(patched_crud: MagicMock, ):
        result = System.read_all_users_ids()
        patched_crud.read_all_users_ids.assert_called_once_with(connection=System.connection, )
        assert result == patched_crud.read_all_users_ids.return_value

    @staticmethod
    def test_gen_bots(mock_public_post_f: MagicMock, ):
        with (
            patch.object(
                System.PublicPostService,
                'get_public_posts',
                return_value=[mock_public_post_f, ],
                autospec=True,
            ) as mock_get_public_posts,
            patch.object(
                System,
                'set_bots_votes_to_post',
                autospec=True,
            ) as mock_set_bots_votes_to_post,
            patch.object(
                System,
                'gen_bot',
                autospec=True,
            ) as mock_gen_bot,
        ):
            System.gen_bots(bots_ids=[1, ], gen_votes=True, )
            mock_get_public_posts.assert_called_once_with(connection=System.connection, )
            mock_set_bots_votes_to_post.assert_called_once_with(post=mock_public_post_f, bots_ids=[1, ], )
            mock_gen_bot.assert_called_once_with(bot_id=1, )

    @staticmethod
    def test_gen_bot(mock_public_post_f: MagicMock, ):
        with patch.object(System.generator, 'gen_new_user', autospec=True, ) as mock_gen_new_user:
            System.gen_bot(bot_id=1, )
        mock_gen_new_user.assert_called_once_with(tg_user_id=1, )
        mock_gen_new_user.return_value.create.assert_called_once_with()


class TestPublicPost:
    @staticmethod
    def test_get_pending_posts():
        with (
            patch.object(
                PublicPost.Mapper.PublicPost,
                'dbs_to_cls',
                autospec=True,
            ) as mock_db_to_cls,
            patch.object(
                PublicPost.Mapper.PublicPost.CRUD,
                'read_public_posts_by_status',
                autospec=True,
            ) as mock_read_posts,
        ):
            result = PublicPost.get_pending_posts(connection=typing_Any, )
        # CHECKS
        mock_read_posts.assert_called_once_with(
            status=PublicPost.Mapper.PublicPost.Status.PENDING,
            connection=typing_Any,
        )
        mock_db_to_cls.assert_called_once_with(
            posts_rows=mock_read_posts.return_value,
            connection=typing_Any,
        )
        assert result == mock_db_to_cls.return_value

    @staticmethod
    def test_get_public_posts():
        with (
            patch.object(PublicPost.Mapper.DB, 'read', autospec=True, return_value=[1, ], ) as db_mock_read,
            patch.object(PublicPost.Mapper.PublicPost, 'read', autospec=True, ) as mock_read,
        ):
            result = PublicPost.get_public_posts(connection=typing_Any, )
        # CHECKS
        db_mock_read.assert_called_once_with(
            statement=PublicPost.Mapper.DB.sqls.PublicPosts.READ_PUBLIC_POSTS_IDS,
            fetch='fetchall',
            connection=typing_Any,
        )
        mock_read.assert_called_once_with(post_id=1, connection=typing_Any, )
        assert result == [mock_read.return_value, ]

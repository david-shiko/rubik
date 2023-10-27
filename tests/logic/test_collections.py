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
from unittest.mock import patch, ANY, create_autospec
from typing import TYPE_CHECKING, Any as typing_Any

import pytest

import app.config

from app.models.posts import PersonalPost
import app.models.users
import app.models.collections
import app.services

if TYPE_CHECKING:
    from unittest.mock import MagicMock

test_cls = app.models.collections.Collection


class TestCollection:

    @staticmethod
    @pytest.fixture(scope='function', )
    def patched_mapper() -> MagicMock:
        with patch.object(app.models.collections.Collection, 'Mapper', autospec=True, ) as mock_mapper:
            yield mock_mapper

    @staticmethod
    @pytest.fixture(scope='function', )
    def patched_crud() -> MagicMock:
        with patch.object(app.models.collections.Collection, 'CRUD', autospec=True, ) as mock_crud:
            yield mock_crud

    class TestDbToCls:

        @staticmethod
        def test_with_author(collection_raw: app.structures.base.CollectionDB, user_s: app.models.users.User, ):
            result = test_cls.db_to_cls(raw_collection=collection_raw, author=user_s, )
            assert vars(result)

        @staticmethod
        def test_without_author(collection_raw: app.structures.base.CollectionDB, ):
            result = test_cls.db_to_cls(raw_collection=collection_raw, )
            assert vars(result)

    @staticmethod
    def test_create(patched_crud: MagicMock, collection: app.models.collections.Collection, ):
        patched_crud.create.return_value = None  # To enter if branch
        test_cls.create(
            author=collection.author,
            name=collection.name,
            posts_ids=[typing_Any],
        )
        patched_crud.create.assert_called_once_with(
            author=collection.author.tg_user_id,
            name=collection.name,
            connection=collection.author.connection,
        )
        patched_crud.read_id_by_name.assert_called_once_with(
            author=collection.author.tg_user_id,
            name=collection.name,
            connection=collection.author.connection,
        )
        patched_crud.create_2m2_collection_post.assert_called_once_with(
            collection_id=patched_crud.read_id_by_name.return_value,
            post_id=typing_Any,
            connection=collection.author.connection,
        )
        assert len(patched_crud.mock_calls) == 3

    @staticmethod
    def test_get_user_collections(
            patched_crud: MagicMock,
            user_s: app.models.users.User,
            collection_raw: app.structures.base.CollectionDB,
    ):
        patched_crud.read_user_collections.return_value = [collection_raw]
        with patch.object(test_cls, 'db_to_cls', autospec=True, ) as mock_db_to_cls:
            result = test_cls.get_user_collections(author=user_s, )
        # Checks
        patched_crud.read_user_collections.assert_called_once_with(
            author=user_s.tg_user_id,
            connection=user_s.connection, )
        mock_db_to_cls.assert_called_once_with(raw_collection=ANY, author=user_s)
        assert result == [mock_db_to_cls.return_value]

    @staticmethod
    def test_read_by_ids_different_authors(
            user_s: app.models.users.User,
            collection_raw: app.structures.base.CollectionDB,
            patched_crud: MagicMock,
            patched_mapper: MagicMock,
    ):
        """read_collections_by_ids"""
        patched_crud.read_by_ids.return_value = [collection_raw]
        # ~ - to not match with main id
        mock_author_1 = create_autospec(tg_user_id=collection_raw['author'], spec=user_s, spec_set=True, )
        mock_author_2 = create_autospec(tg_user_id=~collection_raw['author'], spec=user_s, spec_set=True, )
        mock_author_1.tg_user_id = collection_raw['author']
        mock_author_2.tg_user_id = ~collection_raw['author']
        patched_mapper.User.return_value = mock_author_2
        with patch.object(test_cls, 'db_to_cls', autospec=True, ) as mock_db_to_cls:
            for user in [mock_author_1, mock_author_2, ]:
                result = test_cls.get_by_ids(user=user, ids=[1, 2], )
                # Checks
                patched_crud.read_by_ids.assert_called_once_with(ids=[1, 2], connection=user.connection, )
                mock_db_to_cls.assert_called_once_with(raw_collection=collection_raw, author=user, )
                assert result == [mock_db_to_cls.return_value]
                patched_crud.reset_mock()
                mock_db_to_cls.reset_mock()
        patched_mapper.User.assert_called_once_with(  # Assert called only once of two times when reader != author
            tg_user_id=collection_raw['author'],
            connection=patched_mapper.User.return_value.connection,
        )

    @staticmethod
    @pytest.mark.parametrize(
        argnames='prefix', argvalues=[
            app.services.Collection.NamePrefix.PUBLIC.value,
            app.services.Collection.NamePrefix.PERSONAL.value
        ],
)
    def test_get_defaults(
            user_s: app.models.users.User,
            patched_crud: MagicMock,
            collection_raw: app.structures.base.CollectionDB,
            prefix: str,
    ):
        collection_raw = collection_raw.copy()
        collection_raw['name'] = f"{prefix}_{collection_raw['name']}"  # Imitate name from db
        patched_crud.read_defaults.return_value = [collection_raw]
        with patch.object(test_cls, 'db_to_cls', autospec=True, ) as mock_db_to_cls:
            result = test_cls.get_defaults(author=user_s, prefix=prefix, )
        # Checks
        patched_crud.read_defaults.assert_called_once_with(
            connection=user_s.connection,
            prefix=prefix,
        )
        mock_db_to_cls.assert_called_once_with(
            author=user_s,
            raw_collection=patched_crud.read_defaults.return_value[0],
        )
        assert result == [mock_db_to_cls.return_value]
        patched_crud.reset_mock()

    @staticmethod
    def test_get_posts(
            collection: app.models.collections.Collection,
            patched_crud: MagicMock,
    ):
        """
        read_collection_posts
        """
        with patch.object(app.models.posts.PublicPost, 'dbs_to_cls') as mock_convert_public_posts:
            with patch.object(app.models.posts.PersonalPost, 'dbs_to_cls') as mock_convert_personal_posts:
                result = test_cls.get_posts(
                    author=collection.author,
                    collection_id=collection.collection_id,
                )
        # Checks
        patched_crud.read_posts_public.assert_called_once_with(  # Assert converted public
            collection_id=collection.collection_id,
            connection=collection.author.connection,
        )
        patched_crud.read_posts_personal.assert_called_once_with(  # Assert read personal
            collection_id=collection.collection_id,
            connection=collection.author.connection,
        )
        mock_convert_public_posts.assert_called_once_with(  # Assert converted public
            posts_rows=patched_crud.read_posts_public.return_value,
            connection=collection.author.connection,
        )
        mock_convert_personal_posts.assert_called_once_with(  # Assert converted personal
            posts_rows=patched_crud.read_posts_personal.return_value,
            connection=collection.author.connection,
        )
        assert result == []  # Should br converted posts inside but unpucking MagicMock returns []

    @staticmethod
    @pytest.mark.parametrize(
        argnames='prefix', argvalues=[
            app.services.Collection.NamePrefix.PUBLIC.value,
            app.services.Collection.NamePrefix.PERSONAL.value
        ]
        )
    def test_get_defaults_names(patched_crud: MagicMock, prefix: str, ):
        patched_crud.read_defaults_names.return_value = ['foo']
        result = test_cls.get_defaults_names(prefix=prefix, connection=typing_Any, )
        patched_crud.read_defaults_names.assert_called_once_with(
            connection=typing_Any,
            prefix=prefix,
        )
        assert result == patched_crud.read_defaults_names.return_value

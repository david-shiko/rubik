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

import app.config
import app.db.crud.collections
import app.services

if TYPE_CHECKING:
    from unittest.mock import MagicMock


class TestCollection:
    cls_to_test = app.db.crud.collections.Collection

    @pytest.fixture(scope='function')
    def patched_db(self, ) -> MagicMock:
        with patch.object(self.cls_to_test, 'db', autospec=True, ) as mock_db:
            yield mock_db

    def test_create(self, patched_db: MagicMock, collection: app.models.collections.Collection, ):
        result = self.cls_to_test.create(
            author=collection.author.tg_user_id,
            name=collection.name,
            connection=collection.author.connection,
        )
        patched_db.create.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.Collections.CREATE_COLLECTION,
            values=(collection.author.tg_user_id, collection.name,),
            connection=collection.author.connection,
        )
        assert result == patched_db.create.return_value

    def test_create_2m2_collection_post(self, patched_db: MagicMock, collection: app.models.collections.Collection, ):
        self.cls_to_test.create_2m2_collection_post(
            collection_id=collection.collection_id,
            post_id=1,
            connection=collection.author.connection,
        )
        patched_db.create.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.Collections.CREATE_M2M_COLLECTIONS_POSTS,
            values=(collection.collection_id, 1,),
            connection=collection.author.connection,
        )

    def test_read_id_by_name(self, patched_db: MagicMock, collection: app.models.collections.Collection):
        result = self.cls_to_test.read_id_by_name(
            author=collection.author.tg_user_id,
            name=collection.name,
            connection=collection.author.connection,
        )
        patched_db.read.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.Collections.READ_USER_COLLECTION_ID_BY_NAME,
            values=(collection.author.tg_user_id, collection.name,),
            connection=collection.author.connection,
        )
        assert result == patched_db.read.return_value

    def test_read_collections_by_ids(self, patched_db: MagicMock, ):
        result = self.cls_to_test.read_by_ids(ids=[1, ], connection=typing_Any)
        patched_db.read.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.Collections.READ_COLLECTIONS_BY_IDS,
            values=((1,),),  # list of ids will be converted to tuple
            connection=typing_Any,
            fetch='fetchall'
        )
        assert result == patched_db.read.return_value

    def test_read_user_raw_collections(self, patched_db: MagicMock, user_s: app.models.users.User, ):
        result = self.cls_to_test.read_user_collections(
            author=user_s.tg_user_id,
            connection=user_s.connection,
        )
        patched_db.read.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.Collections.READ_USER_COLLECTIONS,
            values=(user_s.tg_user_id,),
            connection=user_s.connection,
            fetch='fetchall'
        )
        assert result == patched_db.read.return_value

    def test_read_collection_posts_public(self, patched_db: MagicMock, collection: app.models.collections.Collection, ):
        result = self.cls_to_test.read_posts_public(
            collection_id=collection.collection_id,
            connection=collection.author.connection,
        )
        patched_db.read.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.Collections.READ_PUBLIC_COLLECTION_POSTS,
            values=(collection.collection_id,),
            connection=collection.author.connection,
            fetch='fetchall'
        )
        assert result == patched_db.read.return_value

    def test_read_collection_posts_personal(
            self,
            patched_db: MagicMock,
            collection: app.models.collections.Collection,
    ):
        result = self.cls_to_test.read_posts_personal(
            collection_id=collection.collection_id,
            connection=collection.author.connection,
        )
        patched_db.read.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.Collections.READ_PERSONAL_COLLECTION_POSTS,
            values=(collection.collection_id,),
            connection=collection.author.connection,
            fetch='fetchall'
        )
        assert result == patched_db.read.return_value

    @pytest.mark.parametrize(argnames='prefix', argvalues=app.services.Collection.NamePrefix, )
    def test_read_default_collection_names(
            self,
            patched_db: MagicMock,
            collection: app.models.collections.Collection,
            prefix: str,
    ):
        result = self.cls_to_test.read_defaults_names(
            prefix=prefix,
            connection=collection.author.connection,
        )
        patched_db.read.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.Collections.READ_DEFAULT_COLLECTION_NAMES,
            values=(app.config.BOT_ID, prefix,),
            connection=collection.author.connection,
            fetch='fetchall'
        )
        assert result == patched_db.read.return_value

    @pytest.mark.parametrize(argnames='prefix', argvalues=app.services.Collection.NamePrefix, )
    def test_read_defaults(self, patched_db: MagicMock, prefix: str):
        result = self.cls_to_test.read_defaults(
            prefix=prefix,
            connection=typing_Any,
        )

        patched_db.read.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.Collections.READ_DEFAULT_COLLECTIONS,
            values=(app.config.BOT_ID, prefix,),
            connection=typing_Any,
            fetch='fetchall'
        )
        assert result == patched_db.read.return_value

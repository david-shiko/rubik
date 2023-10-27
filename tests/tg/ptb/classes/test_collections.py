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
from unittest.mock import patch, create_autospec

import pytest
# noinspection PyPackageRequirements
from telegram import InlineKeyboardButton as tg_IKB

from app.tg.ptb import services, config
from app.tg.ptb.classes.collections import Collection

if TYPE_CHECKING:
    from app.tg.ptb.classes.users import User


class TestCollection:
    pass


class TestKeyboards:
    class TestShared:
        test_cls = Collection.Keyboards.Shared

        def test_build_inline_button(self, ptb_collection_s: Collection, ):
            mock_keyboard = create_autospec(spec=self.test_cls(collection=ptb_collection_s, ), spec_set=True, )
            result = self.test_cls.build_inline_button(self=mock_keyboard, sender_tg_user_id=1, )
            mock_keyboard.build_callback.assert_called_once_with(sender_tg_user_id=1)
            assert isinstance(result, tg_IKB)
            assert result.text == mock_keyboard.collection.name
            assert result.callback_data == mock_keyboard.build_callback.return_value

    class TestShow:
        test_cls = Collection.Keyboards.Show

        @pytest.fixture
        def keyboard(self, ptb_collection_s: Collection, ) -> Collection.Keyboards.Show:
            yield self.test_cls(collection=ptb_collection_s, )

        def test_build_cbk_data(self, keyboard: Collection.Keyboards.Show, ):
            result = self.test_cls.build_callback(self=keyboard, sender_tg_user_id=1, )
            assert result == f'{config.SHOW_COLLECTION_CBK_S} 1'

        def test_extract_cbk_data(self):
            result = self.test_cls.extract_cbk_data(cbk_data=f'{config.SHOW_COLLECTION_CBK_S} 1', )
            assert result == 1

    class TestMarkAndShow:
        test_cls = Collection.Keyboards.MarkAndShow

        @pytest.fixture
        def keyboard(self, ptb_collection_s: Collection, ) -> Collection.Keyboards.MarkAndShow:
            yield self.test_cls(collection=ptb_collection_s, )

        def test_build_cbk_data(self, keyboard: Collection.Keyboards.MarkAndShow, ):
            result = self.test_cls.build_callback(self=keyboard, sender_tg_user_id=1, )
            assert result == f'{config.MARK_SHOW_COLLECTION_CBK_S} 1'

        def test_extract_cbk_data(self):
            result = self.test_cls.extract_cbk_data(cbk_data=f'{config.MARK_SHOW_COLLECTION_CBK_S} 1', )
            assert result == 1

    class TestShowPostsForRecipient:
        class Shared:
            test_cls = Collection.Keyboards.ShowPostsForRecipient

        test_cls = Shared.test_cls

        @pytest.fixture
        def keyboard(self, ptb_collection_s: Collection, ) -> Collection.Keyboards.ShowPostsForRecipient:
            yield self.test_cls(collection=ptb_collection_s, )

        def test_build_cbk_data(self, keyboard: Collection.Keyboards.ShowPostsForRecipient, ):
            result = self.test_cls.build_callback(self=keyboard, sender_tg_user_id=1, )
            assert result == f'{config.SHOW_COLLECTION_POSTS_CBK_S} {1} {keyboard.collection.collection_id}'

        class TestExtractCbkData(Shared, ):
            def test_with_user(self, ptb_user_s: User, ):
                cbk_data = f"{config.SHOW_COLLECTION_CBK_S} 1 2"
                with patch.object(Collection.Mapper, 'User', autospec=True, ) as mock_user:
                    result = self.test_cls.extract_cbk_data(cbk_data=cbk_data, user=ptb_user_s, )
                assert result == (ptb_user_s, 2,)
                mock_user.assert_not_called()

            def test_without_user(self, ):
                cbk_data = f"{config.SHOW_COLLECTION_CBK_S} 1 2"
                with patch.object(Collection.Mapper, 'User', autospec=True, ) as mock_user:
                    result = self.test_cls.extract_cbk_data(cbk_data=cbk_data, )
                assert result == (mock_user.return_value, 2,)
                mock_user.assert_called_once_with(tg_user_id=1, )

    class TestMark:
        test_cls = Collection.Keyboards.Mark

        @pytest.fixture
        def keyboard(self, ptb_collection_s: Collection, ) -> Collection.Keyboards.Mark:
            yield self.test_cls(collection=ptb_collection_s, )

        def test_build_cbk_data(self, keyboard: Collection.Keyboards.Mark, ):
            result = self.test_cls.build_callback(self=keyboard, sender_tg_user_id=1, )
            assert result == f'{config.MARK_COLLECTION_CBK_S} 1'

        def test_extract_cbk_data(self):
            result = self.test_cls.extract_cbk_data(cbk_data=f'{config.MARK_COLLECTION_CBK_S} 1', )
            assert result == 1

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
from unittest.mock import create_autospec, MagicMock

import pytest

import app.tg.ptb.config
import app.tg.ptb.services

# noinspection PyPackageRequirements
from telegram import InlineKeyboardMarkup as tg_IKM, InlineKeyboardButton as tg_IKB

if TYPE_CHECKING:
    from app.tg.ptb.classes.collections import Collection


class TestCollection:
    @staticmethod
    def test_set(mock_ptb_collection: MagicMock, ):
        app.tg.ptb.services.Collection.Keyboards.set(
            collections=[mock_ptb_collection, ],
            keyboard=mock_ptb_collection.Keyboards.Show  # Show just for example, may be any keyboard from cls
        )
        assert mock_ptb_collection.keyboards.current == mock_ptb_collection.Keyboards.Show.return_value

    class TestKeyboards:

        class TestShow:
            @staticmethod
            @pytest.mark.parametrize(argnames='posts_in_row', argvalues=(1, 2, 3), )
            def test_show_many(
                    ptb_collection_s: Collection,
                    posts_in_row: int,
            ):
                collections = [  # Create dynamically here is ok cuz need pass a check "assert_called_once"
                    create_autospec(spec=ptb_collection_s, spec_set=True, ),
                    create_autospec(spec=ptb_collection_s, spec_set=True, ),
                ]
                result = app.tg.ptb.services.Collection.Keyboards.show_many(
                    sender_tg_user_id=1,
                    collections=collections,
                    posts_in_row=posts_in_row
                )
                for collection in collections:
                    collection.keyboards.current.build_inline_button.assert_called_once_with(
                        sender_tg_user_id=1,
                    )
                for i, row in enumerate(result.inline_keyboard):
                    collections_in_row = collections[i * posts_in_row: (i + 1) * posts_in_row]
                    # Assert that the resulting inline keyboard contains the correct buttons
                    for button, collection in zip(row, collections_in_row):
                        assert button == collection.keyboards.current.build_inline_button(
                            sender_tg_user_id=1,
                        )
                # Assert that the total number of rows matches the expected number.
                # The number of rows is calculated as the ceiling division of the number of collections by posts_in_row
                assert len(result.inline_keyboard) == (len(collections) + posts_in_row - 1) // posts_in_row

    @staticmethod
    def test_get_accept_collections():
        actual_keyboard = app.tg.ptb.services.Collection.Keyboards.accept_collections(
            sender_tg_user_id=1, collections_ids={1, 2, 3}
        )
        expected_keyboard = tg_IKM(
            [
                [
                    tg_IKB(
                        text=app.constants.Shared.Words.DECLINE,
                        callback_data=f'{app.tg.ptb.config.ACCEPT_COLLECTIONS_CBK_S} 1 0',
                    ),
                    tg_IKB(
                        text=app.constants.Shared.Words.ACCEPT,
                        callback_data=f'{app.tg.ptb.config.ACCEPT_COLLECTIONS_CBK_S} 1 1 1 2 3',
                    ),
                ]
            ]
        )
        assert actual_keyboard == expected_keyboard

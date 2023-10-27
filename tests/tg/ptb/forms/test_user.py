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

# noinspection PyPackageRequirements
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import pytest

from app.tg.ptb.config import CHECKBOX_CBK_S
from app.tg.ptb import constants
from app.tg.ptb.forms.user import Target

if TYPE_CHECKING:
    from unittest.mock import MagicMock


class TestTarget:
    @staticmethod
    def test_convert_checkboxes_emojis(ptb_target_s: Target, monkeypatch, ):
        monkeypatch.setattr(ptb_target_s.filters, 'checkboxes', Target.Mapper.Matcher.Filters.Checkboxes(), )
        actual = ptb_target_s.convert_checkboxes_emojis()
        expected = {
            'age': Target.CHECKED_EMOJI_CHECKBOX,
            'photo': Target.UNCHECKED_EMOJI_CHECKBOX,
            'country': Target.UNCHECKED_EMOJI_CHECKBOX,
            'city': Target.UNCHECKED_EMOJI_CHECKBOX,
        }

        assert actual == expected

    @staticmethod
    @pytest.mark.parametrize(
        argnames='checkboxes',
        argvalues=(
                # Not all cases but ok
                Target.Mapper.Matcher.Filters.Checkbox(age=True, photo=True, country=True, city=True, ),
                Target.Mapper.Matcher.Filters.Checkbox(age=False, photo=False, country=False, city=False, )
        ), )
    def test_get_checkboxes_keyboard(mock_ptb_target: MagicMock, checkboxes: Target.Mapper.Matcher.Filters.Checkbox, ):
        mock_ptb_target.filters.checkboxes = checkboxes
        actual_keyboard = Target.get_checkboxes_keyboard(self=mock_ptb_target, )
        expected_keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"{mock_ptb_target.convert_checkboxes_emojis.return_value['age']} "
                             f"{constants.Search.Checkboxes.AGE_SPECIFIED}",
                        callback_data=f"{CHECKBOX_CBK_S} age",
                    ),
                    InlineKeyboardButton(
                        text=f"{mock_ptb_target.convert_checkboxes_emojis.return_value['country']} "
                             f"{constants.Search.Checkboxes.COUNTRY_SPECIFIED}",
                        callback_data=f"{CHECKBOX_CBK_S} country",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=f"{mock_ptb_target.convert_checkboxes_emojis.return_value['city']} "
                             f"{constants.Search.Checkboxes.CITY_SPECIFIED}",
                        callback_data=f"{CHECKBOX_CBK_S} city",
                    ),
                    InlineKeyboardButton(
                        text=f"{mock_ptb_target.convert_checkboxes_emojis.return_value['photo']} "
                             f"{constants.Search.Checkboxes.PHOTO_SPECIFIED}",
                        callback_data=f"{CHECKBOX_CBK_S} photo",
                    ),
                ],
            ]
        )

        assert actual_keyboard.to_dict() == expected_keyboard.to_dict()

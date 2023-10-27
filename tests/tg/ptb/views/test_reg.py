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

from app.tg.ptb import constants, keyboards
from app.tg.ptb.config import PUBLIC_COMMANDS
from app.tg.ptb.views import View
from app.tg.ptb.classes import users as ptb_users

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from app.tg.ptb.classes.users import Profile


class TestWarn:
    @staticmethod
    def test_incorrect_name(mock_tg_view_f: MagicMock, ):
        result = View.Reg.Warn.incorrect_name(self=mock_tg_view_f.reg.warn, )
        mock_tg_view_f.reg.warn.bot.send_message.assert_called_once_with(
            chat_id=mock_tg_view_f.reg.warn.tg_user_id,
            text=constants.Reg.INCORRECT_NAME,
        )
        assert result == mock_tg_view_f.reg.warn.bot.send_message.return_value

    @staticmethod
    def test_incorrect_goal(mock_tg_view_f: MagicMock, ):
        result = View.Reg.Warn.incorrect_goal(self=mock_tg_view_f.reg.warn, )
        mock_tg_view_f.reg.warn.bot.send_message.assert_called_once_with(
            chat_id=mock_tg_view_f.reg.warn.tg_user_id,
            text=constants.Reg.INCORRECT_GOAL,
        )
        assert result == mock_tg_view_f.reg.warn.bot.send_message.return_value

    @staticmethod
    def test_incorrect_gender(mock_tg_view_f: MagicMock, ):
        result = View.Reg.Warn.incorrect_gender(self=mock_tg_view_f.reg.warn, )
        mock_tg_view_f.reg.warn.bot.send_message.assert_called_once_with(
            chat_id=mock_tg_view_f.reg.warn.tg_user_id,
            text=constants.Reg.INCORRECT_GENDER,
        )
        assert result == mock_tg_view_f.reg.warn.bot.send_message.return_value

    @staticmethod
    def test_incorrect_age(mock_tg_view_f: MagicMock, ):
        result = View.Reg.Warn.incorrect_age(self=mock_tg_view_f.reg.warn, )
        mock_tg_view_f.reg.warn.bot.send_message.assert_called_once_with(
            chat_id=mock_tg_view_f.reg.warn.tg_user_id,
            text=constants.Reg.INCORRECT_AGE,
        )
        assert result == mock_tg_view_f.reg.warn.bot.send_message.return_value

    @staticmethod
    def test_incorrect_location(mock_tg_view_f: MagicMock, ):
        result = View.Reg.Warn.incorrect_location(self=mock_tg_view_f.reg.warn, )
        mock_tg_view_f.reg.warn.bot.send_message.assert_called_once_with(
            chat_id=mock_tg_view_f.reg.warn.tg_user_id,
            text=constants.Reg.INCORRECT_LOCATION,
        )
        assert result == mock_tg_view_f.reg.warn.bot.send_message.return_value

    @staticmethod
    def test_no_profile_photos(mock_tg_view_f: MagicMock, ):
        result = View.Reg.Warn.no_profile_photos(self=mock_tg_view_f.reg.warn, )
        mock_tg_view_f.reg.warn.bot.send_message.assert_called_once_with(
            chat_id=mock_tg_view_f.reg.warn.tg_user_id,
            text=constants.Reg.NO_PROFILE_PHOTOS,
        )
        assert result == mock_tg_view_f.reg.warn.bot.send_message.return_value

    @staticmethod
    def test_too_many_photos(mock_tg_view_f: MagicMock, ):
        result = View.Reg.Warn.too_many_photos(self=mock_tg_view_f.reg.warn, keyboard=typing_Any, used_photos=3, )
        mock_tg_view_f.reg.warn.bot.send_message.assert_called_once_with(
            chat_id=mock_tg_view_f.reg.warn.tg_user_id,
            text=constants.Reg.TOO_MANY_PHOTOS.format(USED_PHOTOS=3, ),
            reply_markup=typing_Any
        )
        assert result == mock_tg_view_f.reg.warn.bot.send_message.return_value

    @staticmethod
    def test_incorrect_photo(mock_tg_view_f: MagicMock, ):
        result = View.Reg.Warn.incorrect_photo(self=mock_tg_view_f.reg.warn, keyboard=typing_Any)
        mock_tg_view_f.reg.warn.bot.send_message.assert_called_once_with(
            chat_id=mock_tg_view_f.reg.warn.tg_user_id,
            text=constants.Shared.Warn.INCORRECT_FINISH,
            reply_markup=typing_Any
        )
        assert result == mock_tg_view_f.reg.warn.bot.send_message.return_value

    @staticmethod
    def test_comment_too_long(mock_tg_view_f: MagicMock, ):
        result = View.Reg.Warn.comment_too_long(self=mock_tg_view_f.reg.warn, comment_len=100, )
        mock_tg_view_f.reg.warn.SharedView.Warn.text_too_long.assert_called_once_with(
            max_symbols=ptb_users.User.MAX_COMMENT_LEN,
            used_symbols=100,
        )
        assert result == mock_tg_view_f.reg.warn.SharedView.Warn.text_too_long.return_value

    @staticmethod
    def test_incorrect_end_reg(mock_tg_view_f: MagicMock, ):
        result = View.Reg.Warn.incorrect_end_reg(self=mock_tg_view_f.reg.warn, )
        mock_tg_view_f.reg.warn.bot.send_message.assert_called_once_with(
            chat_id=mock_tg_view_f.reg.warn.tg_user_id,
            text=constants.Reg.END_REG_HELP,
        )
        assert result == mock_tg_view_f.reg.warn.bot.send_message.return_value


def test_say_ok(mock_tg_view_f: MagicMock, ):
    result = View.say_ok(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        text=constants.Shared.Words.OK,
        chat_id=mock_tg_view_f.tg_user_id,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_say_reg_hello(mock_tg_view_f: MagicMock):
    result = View.Reg.say_reg_hello(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Reg.STEP_0,
        reply_markup=keyboards.go_keyboard,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_ask_user_name(mock_tg_view_f: MagicMock):
    result = View.Reg.ask_user_name(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Reg.STEP_1,
        reply_markup=keyboards.ask_user_name(mock_tg_view_f.tg_name),
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_ask_user_goal(mock_tg_view_f: MagicMock):
    result = View.Reg.ask_user_goal(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Reg.STEP_2,
        reply_markup=keyboards.ask_user_goal,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_ask_user_gender(mock_tg_view_f: MagicMock):
    result = View.Reg.ask_user_gender(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Reg.STEP_3,
        reply_markup=keyboards.ask_user_gender,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_ask_user_age(mock_tg_view_f: MagicMock, ):
    result = View.Reg.ask_user_age(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Reg.STEP_4,
        reply_markup=keyboards.ask_user_age,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_ask_user_location(mock_tg_view_f: MagicMock, ):
    result = View.Reg.ask_user_location(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Reg.STEP_5,
        reply_markup=keyboards.ask_user_location,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_ask_user_photos(mock_tg_view_f: MagicMock, ):
    result = View.Reg.ask_user_photos(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Reg.STEP_6,
        reply_markup=keyboards.original_photo_keyboard,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_say_photo_added_success(mock_tg_view_f: MagicMock, ):
    keyboard = keyboards.original_photo_keyboard
    result = View.Reg.say_photo_added_success(self=mock_tg_view_f, keyboard=keyboard, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Reg.PHOTOS_ADDED_SUCCESS,
        reply_markup=keyboard,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_say_photos_removed_success(mock_tg_view_f: MagicMock, ):
    result = View.Reg.say_photos_removed_success(self=mock_tg_view_f, keyboard=typing_Any, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Reg.PHOTOS_REMOVED_SUCCESS,
        reply_markup=typing_Any,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_ask_user_comment(mock_tg_view_f: MagicMock, ):
    result = View.Reg.ask_user_comment(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Reg.STEP_7,
        reply_markup=keyboards.skip_cancel
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_show_user_profile(mock_tg_view_f: MagicMock, ptb_profile_s: Profile, ):
    View.Reg.show_profile(self=mock_tg_view_f, profile=ptb_profile_s, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Reg.HERE_PROFILE_PREVIEW,
        reply_markup=keyboards.ask_user_confirm,
    )


def test_say_success_reg(mock_tg_view_f: MagicMock, ):
    result = View.Reg.say_success_reg(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=f'{constants.Reg.SUCCESS_REG}\n{constants.MORE_ACTIONS}\n{PUBLIC_COMMANDS}',
        reply_markup=keyboards.remove()
    )
    assert result == mock_tg_view_f.bot.send_message.return_value

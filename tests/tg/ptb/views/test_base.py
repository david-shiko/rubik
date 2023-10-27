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

from pytest import mark

from app.tg.ptb import keyboards, constants
from app.tg.ptb.views import View
import app.structures.base
import app.tg.ptb.config

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    # noinspection PyPackageRequirements
    from telegram import Update, ReplyKeyboardMarkup as tg_RKM


class TestWarn:
    @staticmethod
    def test_incorrect_finish(mock_tg_view_f: MagicMock, ):
        result = View.Warn.incorrect_finish(self=mock_tg_view_f.warn, )
        mock_tg_view_f.warn.bot.send_message.assert_called_once_with(
            chat_id=mock_tg_view_f.warn.tg_user_id,
            text=constants.Shared.Warn.INCORRECT_FINISH,
        )
        assert result == mock_tg_view_f.warn.bot.send_message.return_value

    @staticmethod
    def test_text_too_long(mock_tg_view_f: MagicMock, ):
        result = View.Warn.text_too_long(self=mock_tg_view_f.warn, max_symbols=123, used_symbols=123, )
        mock_tg_view_f.warn.bot.send_message.assert_called_once_with(
            chat_id=mock_tg_view_f.warn.tg_user_id,
            text=constants.Shared.Warn.TEXT_TOO_LONG.format(
                MAX_TEXT_LEN=123,
                USED_TEXT_LEN=123,
            ),
            reply_markup=keyboards.cancel
        )
        assert result == mock_tg_view_f.warn.bot.send_message.return_value

    @staticmethod
    def test_unskippable_step(mock_tg_view_f: MagicMock, ):
        result = View.Warn.unskippable_step(self=mock_tg_view_f.warn, )
        mock_tg_view_f.warn.bot.send_message.assert_called_once_with(
            chat_id=mock_tg_view_f.warn.tg_user_id,
            text=constants.Shared.Warn.UNSKIPPABLE_STEP,
        )
        assert result == mock_tg_view_f.warn.bot.send_message.return_value

    @staticmethod
    def test_incorrect_send(mock_tg_view_f: MagicMock, ):
        result = View.Warn.incorrect_send(self=mock_tg_view_f.warn, )
        mock_tg_view_f.warn.bot.send_message.assert_called_once_with(
            chat_id=mock_tg_view_f.warn.tg_user_id,
            text=constants.Shared.Warn.INCORRECT_SEND
        )
        assert result == mock_tg_view_f.warn.bot.send_message.return_value

    @staticmethod
    def test_incorrect_continue(mock_tg_view_f: MagicMock, ):
        result = View.Warn.incorrect_continue(self=mock_tg_view_f.warn, )
        mock_tg_view_f.warn.bot.send_message.assert_called_once_with(
            chat_id=mock_tg_view_f.warn.tg_user_id,
            text=constants.Shared.Warn.INCORRECT_CONTINUE.format(CONTINUE=constants.Shared.Words.CONTINUE, )
        )
        assert result == mock_tg_view_f.warn.bot.send_message.return_value

    @staticmethod
    def test_user_not_found(mock_tg_view_f: MagicMock, ):
        result = View.user_not_found(self=mock_tg_view_f.warn, )
        mock_tg_view_f.warn.bot.send_message.assert_called_once_with(
            chat_id=mock_tg_view_f.warn.tg_user_id,
            text=constants.Shared.Warn.ALAS_USER_NOT_FOUND,
        )
        assert result == mock_tg_view_f.warn.bot.send_message.return_value

    @staticmethod
    def test_incorrect_user(mock_tg_view_f: MagicMock, ):
        result = View.Warn.incorrect_user(self=mock_tg_view_f.warn, )
        mock_tg_view_f.warn.bot.send_message.assert_called_once_with(
            chat_id=mock_tg_view_f.warn.tg_user_id,
            text=constants.Shared.Warn.INCORRECT_USER,
        )
        assert result == mock_tg_view_f.warn.bot.send_message.return_value

    @staticmethod
    def test_nan_help_msg(mock_tg_view_f: MagicMock):
        result = View.Warn.nan_help_msg(self=mock_tg_view_f, )
        mock_tg_view_f.bot.send_message.assert_called_once_with(
            text=f'{constants.Shared.Warn.MISUNDERSTAND}\n{constants.ENTER_THE_NUMBER}',
            chat_id=mock_tg_view_f.tg_user_id
        )
        assert result == mock_tg_view_f.bot.send_message.return_value

    @staticmethod
    def test_unclickable_button(mock_tg_update_f: MagicMock, ):
        result = View.unclickable_button(tooltip=mock_tg_update_f.callback_query, )
        mock_tg_update_f.callback_query.answer.assert_called_once_with(
            text=constants.Shared.Warn.UNCLICKABLE_BUTTON,
            show_alert=True,
        )
        assert result == mock_tg_update_f.callback_query.answer.return_value


class TestRegRequired:

    @staticmethod
    @mark.parametrize(argnames='action', argvalues=app.structures.base.ReqRequiredActions, )
    def test_tooltip(mock_tg_update_f: MagicMock, action: app.structures.base.ReqRequiredActions, ):
        result = View.reg_required(self=typing_Any, tooltip=mock_tg_update_f.callback_query, action=action, )
        mock_tg_update_f.callback_query.answer.assert_called_once_with(text=action.value, show_alert=True, )
        assert result == mock_tg_update_f.callback_query.answer.return_value

    @staticmethod
    @mark.parametrize(argnames='action', argvalues=app.structures.base.ReqRequiredActions, )
    def test_message(mock_tg_view_f: MagicMock, action: app.structures.base.ReqRequiredActions, ):
        result = View.reg_required(self=mock_tg_view_f, action=action, )
        mock_tg_view_f.bot.send_message.assert_called_once_with(
            text=action.value,
            chat_id=mock_tg_view_f.tg_user_id,
            reply_markup=keyboards.reg,
        )
        assert result == mock_tg_view_f.bot.send_message.return_value


def test_say_user_got_share_proposal(mock_tg_view_f: MagicMock, ):
    result = View.say_user_got_share_proposal(self=mock_tg_view_f, recipient_tg_user_id=1, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.USER_GOT_SHARE_PROPOSAL.format(USER_ID=1),
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_say_user_got_request(mock_tg_view_f: MagicMock, ):
    result = View.say_user_got_request_proposal(self=mock_tg_view_f, recipient_tg_user_id=1, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.USER_GOT_REQUEST_PROPOSAL.format(USER_ID=1, ),
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_remove_sharing_button(mock_tg_view_f: MagicMock, tg_update_f: Update, ):
    result = View.CJM.remove_sharing_button(self=mock_tg_view_f.cjm, message=tg_update_f.message, )
    mock_tg_view_f.cjm.shared_view.remove_proposal_message.assert_called_once_with(message_id_to_delete=1, )
    assert result == mock_tg_view_f.cjm.shared_view.remove_proposal_message.return_value


@mark.parametrize(
    argnames='keyword, keyboard',
    argvalues=[
        ('foo', keyboards.cancel_factory(buttons=['foo', ])),
        (constants.Shared.Words.READY, keyboards.ready_cancel),
    ],
)
def test_notify_ready_keyword(mock_tg_view_f: MagicMock, keyword: str, keyboard: tg_RKM, ):
    result = View.notify_ready_keyword(self=mock_tg_view_f, keyword=keyword, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Shared.FOR_READY.format(READY=keyword, ),
        reply_markup=keyboard,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_cancel(mock_tg_view_f: MagicMock, ):
    result = View.cancel(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Shared.Words.CANCELED,
        reply_markup=keyboards.remove(),
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_easter_egg(mock_tg_view_f: MagicMock, ):
    View.easter_egg(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.EASTER_EGG,
        reply_markup=keyboards.remove(),
    )
    mock_tg_view_f.bot.delete_message(
        chat_id=mock_tg_view_f.bot.send_message.return_value.chat_id,
        message_id=mock_tg_view_f.bot.send_message.return_value.message_id,
    )


def test_location_service_error(mock_tg_view_f: MagicMock, ):
    result = View.location_service_error(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Reg.ERROR_LOCATION_SERVICE,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_user_declined_share_proposal(mock_tg_view_f: MagicMock, ):
    result = View.user_declined_share_proposal(
        self=mock_tg_view_f,
        tg_user_id=1,
        decliner_tg_name='foo',
    )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=1,
        text=constants.USER_DECLINED_SHARE_PROPOSAL.format(DECLINER_TG_NAME='foo'),
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_user_declined_request_proposal(mock_tg_view_f: MagicMock, ):
    result = View.user_declined_request_proposal(self=mock_tg_view_f, tg_user_id=2, decliner_tg_name='name', )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=2,
        text=constants.USER_DECLINED_REQUEST_PROPOSAL.format(DECLINER_TG_NAME='name'),
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_remove_proposal_message_with_tg_user_id(mock_tg_view_f: MagicMock, ):
    result = View.remove_proposal_message(self=mock_tg_view_f, message_id_to_delete=1, )
    mock_tg_view_f.bot.delete_message.assert_called_once_with(chat_id=mock_tg_view_f.tg_user_id, message_id=1, )
    assert result == mock_tg_view_f.bot.delete_message.return_value


def test_internal_error(mock_tg_view_f: MagicMock, ):
    result = View.internal_error(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.INTERNAL_ERROR,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value

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
from unittest.mock import patch
# noinspection PyPackageRequirements
from telegram import InlineKeyboardButton as tg_IKB, InlineKeyboardMarkup as tg_IKM

import app.tg.forms.post
import app.tg.ptb.config
import app.tg.ptb.forms.post

if TYPE_CHECKING:
    from unittest.mock import MagicMock


class TestPublicPost:
    @staticmethod
    def test_get_keyboard():
        actual_keyboard = app.tg.ptb.forms.post.PublicPost.get_keyboard()
        expected_keyboard = tg_IKM(
            [[
                tg_IKB(
                    text=f'{app.tg.ptb.forms.post.PublicPost.NEG_EMOJI} 0',
                    callback_data=app.tg.ptb.config.EMPTY_CBK_S,
                ),
                tg_IKB(
                    text=f'{app.tg.ptb.forms.post.PublicPost.POS_EMOJI} 0',
                    callback_data=app.tg.ptb.config.EMPTY_CBK_S,
                ),
            ]]
        )
        assert actual_keyboard == expected_keyboard

    @staticmethod
    def test_send(patched_ptb_bot: MagicMock, mock_ptb_public_post_form: MagicMock, ):
        result = app.tg.ptb.forms.post.PublicPost.send(self=mock_ptb_public_post_form, )
        patched_ptb_bot.copy_message.assert_called_once_with(
            chat_id=mock_ptb_public_post_form.author.tg_user_id,
            from_chat_id=mock_ptb_public_post_form.author.tg_user_id,
            message_id=mock_ptb_public_post_form.message_id,
            reply_markup=mock_ptb_public_post_form.get_keyboard(),
        )
        assert result == patched_ptb_bot.copy_message.return_value

    @staticmethod
    def test_create(patched_ptb_bot: MagicMock, mock_ptb_public_post_form: MagicMock, ):
        original_message_id = mock_ptb_public_post_form.message_id  # Before resending to a store channel
        with patch.object(app.tg.forms.post.PublicPost, 'create', autospec=True, ) as mock_create:
            result = app.tg.ptb.forms.post.PublicPost.create(self=mock_ptb_public_post_form, )
        patched_ptb_bot.copy_message.assert_called_once_with(
            chat_id=mock_ptb_public_post_form.STORE_CHANNEL_ID,
            from_chat_id=mock_ptb_public_post_form.author.tg_user_id,
            message_id=original_message_id,
        )
        assert mock_ptb_public_post_form.message_id == patched_ptb_bot.copy_message.return_value.message_id
        mock_create.assert_called_once_with(mock_ptb_public_post_form)  # Self passed automatically for super
        assert result == mock_create.return_value


class TestPersonalPost:

    @staticmethod
    def test_create(mock_ptb_personal_post_form: MagicMock, patched_ptb_bot: MagicMock, ):
        message_id_before = mock_ptb_personal_post_form.message_id  # SAve value before overriding in the target func
        with patch.object(app.tg.forms.post.PersonalPost, 'create', autospec=True, ) as mock_super_create:
            result = app.tg.ptb.forms.post.PersonalPost.create(self=mock_ptb_personal_post_form, )
        patched_ptb_bot.copy_message.assert_called_once_with(
            chat_id=mock_ptb_personal_post_form.STORE_CHANNEL_ID,
            from_chat_id=mock_ptb_personal_post_form.author.tg_user_id,
            message_id=message_id_before,
        )
        assert mock_ptb_personal_post_form.message_id == patched_ptb_bot.copy_message.return_value.message_id
        mock_super_create.assert_called_once_with(mock_ptb_personal_post_form)
        assert result == mock_super_create.return_value

    @staticmethod
    def test_get_keyboard():
        actual_keyboard = app.tg.ptb.forms.post.PersonalPost.get_keyboard()
        expected_keyboard = tg_IKM(
            [[
                tg_IKB(
                    text=app.tg.ptb.forms.post.PersonalPost.DISLIKE,
                    callback_data=app.tg.ptb.config.EMPTY_CBK_S,
                ),
                tg_IKB(
                    text=app.tg.ptb.forms.post.PersonalPost.LIKE,
                    callback_data=app.tg.ptb.config.EMPTY_CBK_S,
                ),
            ]]
        )
        assert actual_keyboard == expected_keyboard

    @staticmethod
    def test_send(patched_ptb_bot: MagicMock, mock_ptb_personal_post_form: MagicMock, ):
        result = app.tg.ptb.forms.post.PersonalPost.send(self=mock_ptb_personal_post_form, )
        patched_ptb_bot.copy_message.assert_called_once_with(
            chat_id=mock_ptb_personal_post_form.author.tg_user_id,
            from_chat_id=mock_ptb_personal_post_form.author.tg_user_id,
            message_id=mock_ptb_personal_post_form.message_id,
            reply_markup=mock_ptb_personal_post_form.get_keyboard(),
        )
        assert result == patched_ptb_bot.copy_message.return_value

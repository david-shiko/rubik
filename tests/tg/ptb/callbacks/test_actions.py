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
from typing import TYPE_CHECKING, Type
from unittest.mock import patch, ANY

import pytest

import app.structures.base
import app.models.posts
import app.models.users
import app.tg.ptb.config
import app.tg.ptb.actions
import app.tg.ptb.classes.posts
import app.tg.ptb.services
from app.tg.ptb.utils import accept_user

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    # noinspection PyPackageRequirements
    from telegram import Update, Contact


@pytest.mark.skip(reason='Removed?')
def test_show_collection_posts(
        tg_update_f: Update,
        mock_context: MagicMock,
        patched_ptb_collection: MagicMock,
        patched_ptb_post_base: MagicMock,
        monkeypatch,
):
    """show_collection_posts"""
    return_value = (mock_context.user_data.current_user, 1,)
    monkeypatch.setattr(patched_ptb_collection.Keyboards.Show.extract_cbk_data, 'return_value', return_value, )
    # Execution
    with patch.object(app.tg.ptb.services.Post, 'prepare_for_send', autospec=True, ) as mock_prepare_for_send:
        result = app.tg.ptb.actions.show_collection_posts(update=tg_update_f, context=mock_context, )
    # Checks
    patched_ptb_collection.get_posts.assert_called_once_with(
        collection_id=1,
        connection=mock_context.user_data.current_user.connection,
    )
    mock_prepare_for_send.assert_called_once_with(
        posts=patched_ptb_collection.get_posts.return_value,
        clicker=mock_context.user_data.current_user,
        opposite=mock_context.user_data.current_user,
    )
    mock_context.user_data.view.collections.show_collection_posts.assert_called_once_with(
        posts=mock_prepare_for_send.return_value
    )
    assert len(mock_context.user_data.view.mock_calls) == 2
    assert result == tg_update_f.callback_query.answer()


@pytest.mark.skip(reason='Removed')
def test_show_global_collection_posts(
        tg_update_f: Update,
        mock_context: MagicMock,
        patched_collection: MagicMock,
):
    tg_update_f.callback_query.data = '_, 1'
    result = app.tg.ptb.actions.show_global_collection_posts(update=tg_update_f, context=mock_context, )
    patched_collection.get_posts.assert_called_once_with(
        collection_id=1,
        connection=mock_context.user_data.current_user.connection,
    )
    mock_context.user_data.view.collections.show_collection_posts.assert_called_once_with(
        posts=patched_collection.get_posts.return_value,
    )
    assert result


def test_accept_user_handler_incorrect(
        tg_update_f: Update,
        mock_context: MagicMock,
        monkeypatch,
):
    """accept_user_handler"""
    monkeypatch.setattr(tg_update_f.effective_message, 'text', 'foo')
    monkeypatch.setattr(tg_update_f.effective_message, 'contact', None)
    # Execution
    result = app.tg.ptb.actions.accept_user_handler(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.view.warn.incorrect_user.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert result is None


def test_accept_user_handler_contact(
        tg_update_f: Update,
        mock_context: MagicMock,
        tg_contact_s: Contact,
        monkeypatch,
):
    """accept_user_handler"""
    monkeypatch.setattr(tg_update_f.effective_message, 'contact', tg_contact_s, )
    # Execution
    result = app.tg.ptb.actions.accept_user_handler(update=tg_update_f, context=mock_context, )
    # Checks
    assert len(mock_context.user_data.view.mock_calls) == 0
    assert result == 1


def test_accept_user_handler(
        tg_update_f: Update,
        mock_context: MagicMock,
        monkeypatch,
):
    """accept_user_handler"""
    monkeypatch.setattr(tg_update_f.effective_message, 'text', str(tg_update_f.effective_user.id))
    # Execution
    result = app.tg.ptb.actions.accept_user_handler(update=tg_update_f, context=mock_context, )
    # Checks
    assert len(mock_context.user_data.view.mock_calls) == 0
    assert result == 1


def test_check_correct_continue_incorrect(
        tg_update_f: Update,
        mock_context: MagicMock,
        monkeypatch,
):
    """check_correct_continue"""
    monkeypatch.setattr(tg_update_f.effective_message, 'text', 'foo')
    # Execution
    result = app.tg.ptb.actions.check_correct_continue(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.view.warn.incorrect_finish.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert result is False


def test_check_correct_continue(
        tg_update_f: Update,
        mock_context: MagicMock,
        monkeypatch,
):
    """check_correct_continue"""
    monkeypatch.setattr(tg_update_f.effective_message, 'text', app.constants.Shared.Words.FINISH)
    # Execution
    result = app.tg.ptb.actions.check_correct_continue(update=tg_update_f, context=mock_context, )
    # Checks
    assert len(mock_context.user_data.view.mock_calls) == 0
    assert result is True


def test_check_is_collections_chosen_false(mock_context: MagicMock, ):
    """check_is_collections_chosen"""
    # Execution
    result = app.tg.ptb.actions.check_is_collections_chosen(context=mock_context, )
    # Checks
    mock_context.user_data.view.collections.collections_to_share_not_chosen.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert result is False


def test_check_is_collections_chosen_true(mock_context: MagicMock, monkeypatch, ):
    """check_is_collections_chosen"""
    monkeypatch.setattr(mock_context.user_data.tmp_data, 'collections_id_to_share', {1, 2, 3})
    # Execution
    result = app.tg.ptb.actions.check_is_collections_chosen(context=mock_context, )
    # Checks
    assert len(mock_context.user_data.view.mock_calls) == 0
    assert result is True


class TestCheckReg:  # Not in use

    @staticmethod
    def test_true(tg_update_f: Update, mock_context: MagicMock, monkeypatch, ):
        monkeypatch.setattr(mock_context.user_data.current_user, 'is_registered', True, )
        action = app.structures.base.ReqRequiredActions.SET_PUBLIC_VOTE
        # Execution
        result = app.tg.ptb.actions.check_reg(context=mock_context, action=action)
        # Checks
        assert result is True
        assert len(mock_context.user_data.view.mock_calls) == 0
        assert len(mock_context.mock_calls) == 0

    @staticmethod
    def test_false(mock_context: MagicMock, monkeypatch, ):
        monkeypatch.setattr(mock_context.user_data.current_user, 'is_registered', False, )
        action = app.structures.base.ReqRequiredActions.SET_PUBLIC_VOTE
        # Execution
        result = app.tg.ptb.actions.check_reg(context=mock_context, action=action, raise_=False, )
        # Checks
        mock_context.user_data.view.reg_required.assert_called_once_with(action=action, tooltip=None, )
        assert len(mock_context.user_data.view.mock_calls) == 1
        assert len(mock_context.mock_calls) == 1
        assert result is False

    @staticmethod
    def test_false_with_tooltip(tg_update_f: Update, mock_context: MagicMock, monkeypatch, ):
        monkeypatch.setattr(mock_context.user_data.current_user, 'is_registered', False, )
        action = app.structures.base.ReqRequiredActions.SET_PUBLIC_VOTE
        # Execution
        result = app.tg.ptb.actions.check_reg(context=mock_context, action=action, raise_=False, )
        # Checks
        mock_context.user_data.view.reg_required.assert_called_once_with(action=action, tooltip=None, )
        assert len(mock_context.user_data.view.mock_calls) == 1
        assert len(mock_context.mock_calls) == 1
        assert result is False

    @staticmethod
    def test_false_raises(mock_context: MagicMock, monkeypatch, ):
        monkeypatch.setattr(mock_context.user_data.current_user, 'is_registered', False, )
        action = app.structures.base.ReqRequiredActions.SET_PUBLIC_VOTE
        # Execution
        with pytest.raises(expected_exception=app.exceptions.ReqRequired):
            app.tg.ptb.actions.check_reg(context=mock_context, action=action)
        # Checks
        mock_context.user_data.view.reg_required.assert_called_once_with(action=action, tooltip=None)
        assert len(mock_context.user_data.view.mock_calls) == 1
        assert len(mock_context.mock_calls) == 1


class TestCallbackToPostHandler:
    @staticmethod
    def test_error(tg_update_f: Update, mock_context: MagicMock, patched_logger: MagicMock, ):
        tg_update_f.callback_query.data = f'foo _ 1'
        with pytest.raises(app.exceptions.UnknownPostType, ):
            app.tg.ptb.actions.callback_to_post(update=tg_update_f, context=mock_context, )

    @staticmethod
    @pytest.mark.parametrize(
        argnames='cls, pattern',
        argvalues=(
                (app.tg.ptb.classes.posts.PersonalPost, app.tg.ptb.config.PERSONAL_VOTE_CBK_S),
                (app.tg.ptb.classes.posts.BotPublicPost, app.tg.ptb.config.PUBLIC_VOTE_CBK_S),
                (app.tg.ptb.classes.posts.ChannelPublicPost, app.tg.ptb.config.CHANNEL_PUBLIC_VOTE_CBK_S),
        ), )
    def test_not_found(
            tg_update_f: Update,
            mock_context: MagicMock,
            patched_logger: MagicMock,
            cls: Type,
            pattern: str,
    ):
        tg_update_f.callback_query.data = f'{pattern} _ 1'
        with patch.object(
                cls,
                'callback_to_post',
                autospec=True,
                side_effect=app.exceptions.PostNotFound,
        ) as mock_callback_to_post:
            result = app.tg.ptb.actions.callback_to_post(update=tg_update_f, context=mock_context, )
        mock_callback_to_post.assert_called_once_with(
            callback=tg_update_f.callback_query,
            connection=mock_context.user_data.current_user.connection,
        )
        patched_logger.error.assert_called_once_with(ANY, )  # ANY cuz run time instance of e will be passed to logger
        mock_context.user_data.view.posts.post_to_vote_not_found.assert_called_once_with(
            tooltip=tg_update_f.callback_query,
        )
        assert result is None

    @staticmethod
    @pytest.mark.parametrize(
        argnames='cls, pattern',
        argvalues=(
                (app.tg.ptb.classes.posts.PersonalPost, app.tg.ptb.config.PERSONAL_VOTE_CBK_S),
                (app.tg.ptb.classes.posts.BotPublicPost, app.tg.ptb.config.PUBLIC_VOTE_CBK_S),
                (app.tg.ptb.classes.posts.ChannelPublicPost, app.tg.ptb.config.CHANNEL_PUBLIC_VOTE_CBK_S),
        ), )
    def test_found(tg_update_f: Update, mock_context: MagicMock, cls: Type, pattern: str, ):
        tg_update_f.callback_query.data = f'{pattern} _ 1'
        with patch.object(cls, 'callback_to_post', autospec=True, ) as mock_callback_to_post:
            result = app.tg.ptb.actions.callback_to_post(update=tg_update_f, context=mock_context, )
        mock_callback_to_post.assert_called_once_with(
            callback=tg_update_f.callback_query,
            connection=mock_context.user_data.current_user.connection,
        )
        assert result == mock_callback_to_post.return_value


class TestAcceptUser:
    """
    test_accept_user
    HEre cuz no file for test ptb utils :)
    """

    @staticmethod
    def test_text(tg_update_f: Update, ):
        expected_user_id = tg_update_f.effective_message.from_user.id
        tg_update_f.effective_message.text = str(expected_user_id)
        assert accept_user(message=tg_update_f.effective_message) == expected_user_id

    @staticmethod
    def test_text_check(patched_ptb_bot: MagicMock, tg_update_f: Update, ):
        expected_user_id = tg_update_f.effective_message.from_user.id
        tg_update_f.effective_message.text = str(expected_user_id)
        assert accept_user(message=tg_update_f.effective_message, check=True, ) == expected_user_id
        patched_ptb_bot.get_chat.assert_called_once_with(chat_id=tg_update_f.effective_message.chat_id, )

    @staticmethod
    def test_contact(tg_update_f: Update, tg_contact_s: Contact, monkeypatch, ):
        expected_user_id = tg_update_f.effective_message.from_user.id
        monkeypatch.setattr(tg_update_f.effective_message, 'contact', tg_contact_s)
        assert accept_user(message=tg_update_f.effective_message) == expected_user_id
        monkeypatch.setattr(tg_update_f.effective_message.contact, 'user_id', None)
        assert accept_user(message=tg_update_f.effective_message) is None

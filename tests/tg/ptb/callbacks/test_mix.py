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
from pprint import pformat as pprint_pformat

import pytest
# noinspection PyPackageRequirements
from telegram import Update as tg_Update
# noinspection PyPackageRequirements
from telegram.error import Unauthorized as tg_error_Unauthorized

import app.exceptions
import app.generation

import app.tg.ptb.handlers.mix
import app.tg.ptb.utils
import app.tg.ptb.config

if TYPE_CHECKING:
    from unittest.mock import MagicMock

TEST_MODULE = app.tg.ptb.handlers.mix


@pytest.fixture(scope='module', )
def patched_mix() -> MagicMock:
    with patch.object(app.models, 'mix', autospec=True, ) as patched_mix:
        # Only MagicMock has "__iter__" method
        # See https://stackoverflow.com/q/74837862/14190526
        yield patched_mix


@pytest.fixture(scope='module', )
def patched_utils() -> MagicMock:
    with patch.object(app.tg.ptb, 'utils', autospec=True, ) as patched_utils:
        yield patched_utils


class TestGetStatisticWith:

    @staticmethod
    def test_entry_point(mock_context: MagicMock, ):
        result = app.tg.ptb.handlers.mix.GetStatisticWith.entry_point(_=typing_Any, context=mock_context, )
        mock_context.user_data.view.cjm.say_statistic_hello.assert_called_once_with()
        assert len(mock_context.user_data.view.mock_calls) == 1
        assert result == 0

    class TestEntryPointHandler:
        """entry_point_handler"""

        @staticmethod
        def test_incorrect_user(
                tg_update_f: tg_Update,
                mock_context: MagicMock,
                patched_utils: MagicMock,
                monkeypatch,
        ):
            monkeypatch.setattr(patched_utils.accept_user, 'return_value', None)
            # Execution
            result = app.tg.ptb.handlers.mix.GetStatisticWith.entry_point_handler(
                update=tg_update_f,
                context=mock_context,
            )
            # Checks
            patched_utils.accept_user.assert_called_once_with(message=tg_update_f.message)
            mock_context.user_data.view.warn.incorrect_user.assert_called_once_with()
            assert len(mock_context.user_data.view.mock_calls) == 1
            assert result is None

        @staticmethod
        def test_user_not_found(
                tg_update_f: tg_Update,
                mock_context: MagicMock,
                patched_utils: MagicMock,
                patched_mix: MagicMock,
                monkeypatch,
        ):
            with_tg_user_id = 2
            monkeypatch.setattr(patched_utils.accept_user, 'return_value', with_tg_user_id)
            monkeypatch.setattr(
                mock_context.user_data.view.cjm.show_statistic,
                'side_effect',
                tg_error_Unauthorized(''),
            )
            # Execution
            result = app.tg.ptb.handlers.mix.GetStatisticWith.entry_point_handler(
                update=tg_update_f,
                context=mock_context,
            )
            patched_mix.MatchStats.assert_called_once_with(
                user=mock_context.user_data.current_user,
                with_tg_user_id=with_tg_user_id,
            )
            mock_context.user_data.view.cjm.show_statistic.assert_called_once_with(
                match_stats=patched_mix.MatchStats.return_value,
            )
            mock_context.user_data.view.user_not_found.assert_called_once_with()
            assert len(mock_context.user_data.view.mock_calls) == 2
            assert result is None
            patched_mix.reset_mock()

        @staticmethod
        def test_success(
                tg_update_f: tg_Update,
                mock_context: MagicMock,
                patched_utils: MagicMock,
                patched_mix: MagicMock,
                monkeypatch,
        ):
            with_tg_user_id = 2
            monkeypatch.setattr(patched_utils.accept_user, 'return_value', with_tg_user_id)
            # Execution
            result = app.tg.ptb.handlers.mix.GetStatisticWith.entry_point_handler(
                update=tg_update_f,
                context=mock_context,
            )
            patched_mix.MatchStats.assert_called_once_with(
                user=mock_context.user_data.current_user,
                with_tg_user_id=with_tg_user_id,
            )
            mock_context.user_data.view.cjm.show_statistic.assert_called_once_with(
                match_stats=patched_mix.MatchStats.return_value,
            )
            assert len(mock_context.user_data.view.mock_calls) == 1
            assert result == patched_utils.end_conversation.return_value
            patched_mix.reset_mock()


def test_faq(mock_context: MagicMock, ):
    result = app.tg.ptb.handlers.mix.faq(_=typing_Any, context=mock_context, )
    mock_context.user_data.view.cjm.faq.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert result is None


def test_all_bot_commands_handler_handler(mock_context: MagicMock, ):
    result = app.tg.ptb.handlers.mix.all_bot_commands_handler(_=typing_Any, context=mock_context, )
    mock_context.user_data.view.cjm.show_bot_commands.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert result is None


def test_personal_example(mock_context: MagicMock, patched_mix: MagicMock, ):
    result = app.tg.ptb.handlers.mix.personal_example(_=typing_Any, context=mock_context, )
    patched_mix.MatchStats.assert_called_once_with(
        user=mock_context.user_data.current_user,
        with_tg_user_id=123456,
        set_statistic=False,
    )
    patched_mix.MatchStats.return_value.fill_random.assert_called_once_with()
    mock_context.user_data.view.cjm.show_statistic.assert_called_once_with(
        match_stats=patched_mix.MatchStats.return_value,
    )
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert result is None


def test_auto_deb_logger(mock_context: MagicMock, mock_tg_update_f: tg_Update, monkeypatch, ):
    mock_tg_update_f.effective_message.text = 'Test text'
    mock_tg_update_f.effective_message.effective_attachment = 'Test attachment'
    mock_tg_update_f.callback_query.data = 'Test data'
    monkeypatch.setattr(mock_context, 'user_data', {'Test user data': 'Test user value'}, )
    monkeypatch.setattr(mock_context, 'chat_data', {'Test chat data': 'Test chat value'}, )
    monkeypatch.setattr(mock_context, 'bot_data', {'Test bot data': 'Test bot value'}, )
    monkeypatch.setattr(app.tg.ptb.config.Config, 'is_log', True)
    app.tg.ptb.handlers.mix.auto_deb_logger(update=mock_tg_update_f, context=mock_context, )
    expected_log_data = {
        "message_text": 'Test text',
        "message_attachment": 'Test attachment',
        "callback_data": 'Test data',
        "user_data": {'Test user data': 'Test user value'},
        "chat_data": {'Test chat data': 'Test chat value'},
        "bot_data": {'Test bot data': 'Test bot value'},
    }
    expected_arg = '\n' + pprint_pformat(expected_log_data)
    app.tg.ptb.config.Config.logger.debug.assert_called_once_with(expected_arg)


class TestGenBotsHandlerCmd:
    @staticmethod
    def test_get_num_from_text_raises_value_error(mock_tg_update_f: MagicMock, mock_context: MagicMock, ):
        with (
            patch.object(
                app.utils,
                'get_num_from_text',
                autospec=True,
                side_effect=ValueError,
            ) as mock_get_num_from_text,
            patch.object(app.utils, 'limit_num', autospec=True, ) as mock_limit_num,
        ):
            app.tg.ptb.handlers.mix.gen_bots_handler_cmd(update=mock_tg_update_f, context=mock_context, )
            mock_get_num_from_text.assert_called_once_with(text=mock_tg_update_f.effective_message.text, )
            mock_context.user_data.view.warn.nan_help_msg.assert_called_once_with()
            mock_limit_num.assert_not_called()

    @staticmethod
    def test_valid_number_in_message(mock_tg_update_f: MagicMock, mock_context: MagicMock, ):
        with (
            patch.object(
                app.utils,
                'get_num_from_text',
                autospec=True,
            ) as mock_get_num_from_text,
            patch.object(app.utils, 'limit_num', autospec=True, return_value=5, ) as mock_limit_num,
            patch.object(TEST_MODULE.services.System, 'gen_bots', autospec=True, ) as mock_gen_bots,
        ):
            app.tg.ptb.handlers.mix.gen_bots_handler_cmd(update=mock_tg_update_f, context=mock_context)
            mock_get_num_from_text.assert_called_once_with(text=mock_tg_update_f.effective_message.text, )
            mock_limit_num.assert_called_once_with(num=mock_get_num_from_text.return_value, min_num=1, max_num=99, )
            mock_gen_bots.assert_called_once_with(bots_ids=list(range(mock_limit_num.return_value)), )
            mock_context.user_data.view.say_ok.assert_called_once_with()


def test_log_call_stack_handler():
    """Do nothing currently"""
    app.tg.ptb.handlers.mix.log_call_stack_handler(_=typing_Any, __=typing_Any, )


class TestLogUpdateHandler:
    """log_update_handler"""

    @staticmethod
    def test_photo_with_caption(mock_tg_update_f: MagicMock, ):  # If photo (photo always is list)
        mock_tg_update_f.effective_message.effective_attachment = ['Test attachment']  # Make this a list
        with patch.object(app.tg.ptb.config.Config.view_logger, 'debug', autospec=True, ) as mock_debug:
            app.tg.ptb.handlers.mix.log_update_handler(update=mock_tg_update_f, _=typing_Any, )
        type_ = type(mock_tg_update_f.effective_message.effective_attachment[0]).__name__
        expected_content = f"{type_}:{mock_tg_update_f.effective_message.caption}"
        expected_arg = f'{mock_tg_update_f.effective_user.id}:{expected_content}'
        mock_debug.assert_called_once_with(expected_arg, )

    @staticmethod
    def test_attachment_not_photo(mock_tg_update_f: MagicMock):
        with patch.object(app.tg.ptb.config.Config.view_logger, 'debug', autospec=True, ) as mock_debug:
            app.tg.ptb.handlers.mix.log_update_handler(update=mock_tg_update_f, _=typing_Any)
        type_ = type(mock_tg_update_f.effective_message.effective_attachment).__name__
        expected_arg = f'''{mock_tg_update_f.effective_user.id}:{type_}:{mock_tg_update_f.effective_message.caption}'''
        mock_debug.assert_called_once_with(expected_arg)

    @staticmethod
    def test_text(mock_tg_update_f: MagicMock):
        mock_tg_update_f.effective_message.effective_attachment = None  # Set explicitly to pass a check
        with patch.object(app.tg.ptb.config.Config.view_logger, 'debug', autospec=True, ) as mock_debug:
            app.tg.ptb.handlers.mix.log_update_handler(update=mock_tg_update_f, _=typing_Any)
        expected_arg = f'''{mock_tg_update_f.effective_user.id}:Text:{mock_tg_update_f.effective_message.text}'''
        mock_debug.assert_called_once_with(expected_arg)


class TestError:
    """error_handler"""

    @staticmethod
    def test_error_known(mock_context: MagicMock, patched_logger: MagicMock, ):
        mock_context.error = app.exceptions.NoVotes()  # Any known error is ok
        app.tg.ptb.handlers.mix.error_handler(_=typing_Any, context=mock_context, )
        patched_logger.assert_not_called()


def test_unclickable_cbk_handler(mock_context: MagicMock, tg_update_s: tg_Update, ):
    app.tg.ptb.handlers.mix.unclickable_cbk_handler(update=tg_update_s, context=mock_context, )
    mock_context.user_data.view.unclickable_button.assert_called_once_with(tooltip=tg_update_s.callback_query, )
    assert len(mock_context.mock_calls) == 1


def test_cancel(mock_context: MagicMock, ):
    app.tg.ptb.handlers.mix.cancel(_=typing_Any, context=mock_context, )
    mock_context.user_data.view.cancel.assert_called_once_with()
    assert len(mock_context.mock_calls) == 1

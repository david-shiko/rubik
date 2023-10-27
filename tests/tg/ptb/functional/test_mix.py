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
from typing import TYPE_CHECKING, cast
from unittest.mock import Mock
from logging import CRITICAL as LOGGING_CRITICAL

import pytest
# noinspection PyPackageRequirements
from telegram import Update as tg_Update
# noinspection PyPackageRequirements
from telegram.ext import Dispatcher as tg_Dispatcher, TypeHandler as tg_TypeHandler

import app.tg.ptb.config
import app.tg.ptb.handlers_definition

from tests.tg.ptb.functional.utils import (
    set_command_to_tg_message,
)

if TYPE_CHECKING:
    from unittest.mock import MagicMock


class TestGetStatisticWithHandler:

    @staticmethod
    def test_entry_point(
            tg_update_f: tg_Update,
            tg_dispatcher: tg_Dispatcher,
    ):
        set_command_to_tg_message(tg_message=tg_update_f.message, cmd_text=app.tg.ptb.config.GET_STATISTIC_WITH_S)
        tg_dispatcher.process_update(update=tg_update_f)
        app.tg.ptb.handlers_definition.GetStatisticWithCH.entry_point.callback.assert_called_once()

    @staticmethod
    @pytest.mark.parametrize(argnames='text', argvalues=['-1', '+1', 'foo', 'foo bar'])  # users ids
    def test_entry_point_handler_triggered(
            tg_update_f: tg_Update,
            tg_dispatcher: tg_Dispatcher,
            text: str,
            monkeypatch,
    ):
        handler = app.tg.ptb.handlers_definition.GetStatisticWithCH.CH
        handler.conversations[(tg_update_f.effective_chat.id, tg_update_f.effective_user.id)] = 0
        monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
        tg_dispatcher.process_update(update=tg_update_f)
        mock_callback = app.tg.ptb.handlers_definition.GetStatisticWithCH.entry_point_handler.callback
        mock_callback.assert_called_once()
        mock_callback.reset_mock()  # Reset for parametrize


def test_all_bot_commands_handler_cmd(tg_update_f: tg_Update, tg_dispatcher: tg_Dispatcher):
    set_command_to_tg_message(tg_message=tg_update_f.message, cmd_text=app.tg.ptb.config.ALL_BOT_COMMANDS_S)
    tg_dispatcher.process_update(update=tg_update_f)
    app.tg.ptb.handlers_definition.help_handler_cmd.callback.assert_called_once()


def test_faq_cmd(tg_update_f: tg_Update, tg_dispatcher: tg_Dispatcher):
    set_command_to_tg_message(tg_message=tg_update_f.message, cmd_text=app.tg.ptb.config.FAQ_S)
    tg_dispatcher.process_update(update=tg_update_f)
    app.tg.ptb.handlers_definition.faq_handler_cmd.callback.assert_called_once()


def test_error_handler(tg_update_f: tg_Update, tg_dispatcher: tg_Dispatcher, patched_logger: MagicMock, caplog, ):
    # Add broken handler to dispatcher that will 100% cause ZeroDivision error
    broken_handler = tg_TypeHandler(type=tg_Update, callback=lambda *args, **kwargs: 1 / 0)
    tg_dispatcher.add_handler(handler=broken_handler, group=-100)
    # (just patching logger will not help because error handler is called by dispatcher)
    caplog.set_level(LOGGING_CRITICAL)  # Suppress logs only during test
    tg_dispatcher.process_update(update=tg_update_f)
    tg_dispatcher.remove_handler(handler=broken_handler, group=-100)
    for mock_callback in tg_dispatcher.error_handlers.keys():
        mock_callback = cast(Mock, mock_callback)
        mock_callback.assert_called_once()  # What if multiple error handlers? ...
        mock_callback.reset_mock()  # To pass tear down checks that error handlers was not called
    assert len(patched_logger.mock_calls) == 1

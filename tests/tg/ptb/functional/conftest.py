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
from unittest.mock import create_autospec, Mock  # Mock for isinstance
from typing import TYPE_CHECKING

from pytest import fixture

from custom_ptb.conversation_handler import ConversationHandler
import app.tg.ptb.handlers_definition
import app.tg.ptb.ptb_app

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    # noinspection PyPackageRequirements
    from telegram.ext import Dispatcher, Handler


def get_ch_handlers(ch: ConversationHandler, ) -> list[Handler]:
    result = []
    for handler in (
            ch.entry_points +
            ch.prefallbacks +
            [handler for state_handler in [*ch.states.values()] for handler in state_handler] +
            ch.fallbacks
    ):
        if isinstance(handler, ConversationHandler):  # state handler may be also CH
            result += get_ch_handlers(handler)  # Recursion
        else:
            result.append(handler)
    return result


@fixture(scope='session')
def tg_dispatcher(mock_ptb_bot_s: MagicMock, ) -> Dispatcher:
    """Mck dispatcher handler (Only check that they were called)"""
    updater = app.tg.ptb.ptb_app.create_ptb_app(bot=mock_ptb_bot_s, )
    mocked_error_handlers = {}
    for func, run_async in updater.dispatcher.error_handlers.items():  # Error handlers is just list of func
        mocked_func = create_autospec(spec=func, spec_set=True, side_effect=lambda _, context: func(_, context), )
        mocked_error_handlers[mocked_func] = run_async
    updater.dispatcher.error_handlers = mocked_error_handlers
    callbacks_to_mock = []
    for group_handlers in updater.dispatcher.handlers.values():  # Collect stage
        for i, group_handler in enumerate(group_handlers):
            if isinstance(group_handler, ConversationHandler):
                callbacks_to_mock += get_ch_handlers(ch=group_handler, )
            else:
                callbacks_to_mock.append(group_handler)
    for handler in callbacks_to_mock:  # Mocking stage
        if not isinstance(handler.callback, Mock):
            # Failed to use create_autospec for age_handler, probably because of crate_autospec internal bug
            handler.callback = Mock(spec_set=handler.callback, )
    yield updater.dispatcher

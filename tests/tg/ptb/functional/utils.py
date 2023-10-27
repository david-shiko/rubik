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
from telegram import MessageEntity

from app.constants import Shared

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    # noinspection PyPackageRequirements
    from telegram import Message, Update
    # noinspection PyPackageRequirements
    from telegram.ext import Dispatcher, ConversationHandler


def set_command_to_tg_message(tg_message: Message, cmd_text: str) -> Message:
    command_text = f'/{cmd_text}' if not cmd_text.startswith('/') else cmd_text
    tg_message.entities = [MessageEntity(type=MessageEntity.BOT_COMMAND, offset=0, length=len(command_text))]
    tg_message.text = command_text
    return tg_message


def get_text_cases(texts: list[str], upper: bool = True, lower: bool = True) -> list[str]:
    result = []
    if isinstance(texts, str):
        raise TypeError('Expected list or tuple, got str')  # pragma: no cover
    for text in texts:
        if upper is True:
            result.append(text.upper())
        if lower is True:
            result.append(text.lower())
        result.append(text.capitalize())
        result.append(text.title())
    return result


def cancel_body(
        update: Update,
        dispatcher: Dispatcher,
        ch: ConversationHandler,
        callback: MagicMock,
        monkeypatch,
):
    monkeypatch.setattr(update.effective_message, 'text', Shared.Words.CANCEL)
    ch.conversations[(update.effective_chat.id, update.effective_user.id)] = 0
    monkeypatch.setattr(callback, 'return_value', -1)
    dispatcher.process_update(update=update, )
    callback.assert_called_once()

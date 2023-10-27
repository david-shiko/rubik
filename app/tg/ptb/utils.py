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
from telegram.ext import ConversationHandler

import app.tg.ptb.config

if TYPE_CHECKING:
    # noinspection PyPackageRequirements
    from telegram import Message


def end_conversation() -> int:  # Move to ptb
    return ConversationHandler.END


def accept_user(message: Message, check: bool = False) -> int | None:
    """
    Request a recipient (user) to send a message from a sender (user) to this user
    """
    if message.contact:
        return message.contact.user_id  # It may be None
    elif tg_user_id := ''.join([letter for letter in message.text if letter.isdigit()]):
        tg_user_id = int(tg_user_id)
        if check:
            app.tg.ptb.config.Config.bot.get_chat(chat_id=tg_user_id)  # If not exists - telegram.error.TelegramError
        return tg_user_id

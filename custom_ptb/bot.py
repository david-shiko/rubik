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
# noinspection PyPackageRequirements
from telegram import Message
# noinspection PyPackageRequirements
from telegram.ext import ExtBot

# noinspection PyPep8Naming

"""The class not in use"""


class CustomExtBot(ExtBot):

    # def __init__(self, bot_class: bool = ExtBot, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    @staticmethod
    def accept_user(message: Message) -> int | None:  # Not in use from this object
        """
        Request a recipient (user) to send a message from a sender (user) to this user
        """
        if message.contact:
            return message.contact.user_id
        elif tg_user_id := ''.join([letter for letter in message.text if letter.isdigit()]):
            return int(tg_user_id)
        # elif update.message.text.startswith('@'):
        # Not in use, see https://github.com/python-telegram-bot/ptbcontrib/tree/main/ptbcontrib/username_to_chat_api
        # return self.get_chat(chat_id=update.message.text).id

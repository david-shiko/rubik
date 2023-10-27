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
from typing import cast

# noinspection PyPackageRequirements
from telegram import Update
# noinspection PyPackageRequirements
from telegram.ext import CallbackContext, Dispatcher

from app.tg.ptb.structures import CustomUserData
from app.tg.ptb.views import View
from app.tg.ptb.services import User


class CustomCallbackContext(CallbackContext[CustomUserData, dict, dict]):
    """Custom class for context."""

    def __init__(self, dispatcher: Dispatcher):
        super().__init__(dispatcher=dispatcher)

    @classmethod
    def from_update(cls, update: object, dispatcher: Dispatcher, ) -> CustomCallbackContext:
        context = super().from_update(update, dispatcher, )
        if update is not None and isinstance(update, Update):  # Some attrs may be assigned even without update, do it?
            current_user = context.user_data.current_user = (
                    context.user_data.current_user or
                    User.create_from_update(update=update, )
            )
            context.user_data.view = (
                    context.user_data.view or
                    View(user=current_user, bot=context.bot, )
            )
        return cast(CustomCallbackContext, context)

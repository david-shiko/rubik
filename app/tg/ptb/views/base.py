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
from functools import wraps as functools_wraps
from typing import TYPE_CHECKING, TypeVar, Callable, Any
# noinspection PyPackageRequirements
from telegram.ext import ExtBot

import app.structures.base

from app.tg.ptb import keyboards, constants
from app.tg.ptb.config import Config
from app.tg.ptb.classes.users import User

if TYPE_CHECKING:
    # noinspection PyPackageRequirements
    from telegram import (
        Bot,
        Message,
        CallbackQuery,
    )

R = TypeVar('R')


def log(function: Callable[..., R]) -> Callable[..., R]:
    @functools_wraps(function)
    def wrapper(*args: tuple[Any], **kwargs: dict[str, Any]) -> R:
        result = function(*args, **kwargs)
        msg = getattr(result, 'text', None) or getattr(result, 'effective_attachment', None)
        if msg is None:
            Config.view_logger.debug(msg=function.__name__)
        else:
            Config.view_logger.debug(msg=f'{msg} - {function.__name__}')
        return result

    return wrapper


class Base:

    def __init__(self, user: User, bot: Bot | ExtBot, ):
        self.bot: Bot | ExtBot = bot
        self.tg_user_id = user.tg_user_id
        self.tg_name = user.tg_name


class Shared(Base, ):
    def __init__(self, user: User, bot: Bot | ExtBot, ):
        super().__init__(bot=bot, user=user, )
        self.warn = self.Warn(user=user, bot=bot, )

    class Warn(Base, ):
        @log
        def incorrect_finish(self, ) -> Message:
            return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Shared.Warn.INCORRECT_FINISH, )

        @log
        def text_too_long(self, max_symbols: int, used_symbols: int, ):
            return self.bot.send_message(
                chat_id=self.tg_user_id,
                text=constants.Shared.Warn.TEXT_TOO_LONG.format(MAX_TEXT_LEN=max_symbols, USED_TEXT_LEN=used_symbols, ),
                reply_markup=keyboards.cancel
            )

        @log
        def unskippable_step(self, ) -> Message:
            return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Shared.Warn.UNSKIPPABLE_STEP, )

        @log
        def incorrect_send(self, ) -> Message:
            return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Shared.Warn.INCORRECT_SEND, )

        @log
        def incorrect_continue(self, keyword: str = constants.Shared.Words.CONTINUE, ) -> Message:
            return self.bot.send_message(
                chat_id=self.tg_user_id,
                text=constants.Shared.Warn.INCORRECT_CONTINUE.format(CONTINUE=keyword, ),
            )

        @log
        def incorrect_user(self, ) -> Message:
            return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Shared.Warn.INCORRECT_USER, )

        @log
        def nan_help_msg(self, ) -> Message:  # Not in use
            return self.bot.send_message(
                text=f'{constants.Shared.Warn.MISUNDERSTAND}\n{constants.ENTER_THE_NUMBER}',
                chat_id=self.tg_user_id
            )

    @log
    def say_ok(self, ) -> Message:
        return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Shared.Words.OK, )

    @log
    def notify_ready_keyword(
            self,
            keyword: str = constants.Shared.Words.READY,
    ) -> Message:
        keyboard = keyboards.ready_cancel
        if keyword != constants.Shared.Words.READY:
            # noinspection PyArgumentList
            keyboard = keyboards.cancel_factory(buttons=[keyword, ])
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.Shared.FOR_READY.format(READY=keyword, ),
            reply_markup=keyboard,
        )

    @log
    def cancel(self, ) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.Shared.Words.CANCELED,
            reply_markup=keyboards.remove(),
        )

    @log
    def location_service_error(self, ) -> Message:
        return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Reg.ERROR_LOCATION_SERVICE, )

    @log
    def user_not_found(self, ) -> Message:
        return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Shared.Warn.ALAS_USER_NOT_FOUND, )

    @staticmethod
    @log
    def unclickable_button(tooltip: CallbackQuery, ) -> bool:
        return tooltip.answer(text=constants.Shared.Warn.UNCLICKABLE_BUTTON, show_alert=True, )

    @log
    def reg_required(
            self,
            action: app.structures.base.ReqRequiredActions = app.structures.base.ReqRequiredActions.DEFAULT,
            tooltip: CallbackQuery | None = None,
    ) -> Message | bool:
        """Use command as action, like config.CREATE_PERSONAL_POST_S"""
        text = action.value
        if tooltip:
            return tooltip.answer(text=text, show_alert=True, )  # Show just tooltip
        return self.bot.send_message(chat_id=self.tg_user_id, text=text, reply_markup=keyboards.reg, )

    @log
    def easter_egg(self, ) -> None:
        sent_message = self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.EASTER_EGG,
            reply_markup=keyboards.remove(),
        )
        self.bot.delete_message(chat_id=sent_message.chat_id, message_id=sent_message.message_id, )

    @log
    def say_user_got_share_proposal(self, recipient_tg_user_id: int, ):
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.USER_GOT_SHARE_PROPOSAL.format(USER_ID=recipient_tg_user_id, )
        )

    @log
    def say_user_got_request_proposal(self, recipient_tg_user_id: int, ) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.USER_GOT_REQUEST_PROPOSAL.format(USER_ID=recipient_tg_user_id, ),
        )

    @log
    def user_declined_share_proposal(self, tg_user_id: int, decliner_tg_name: str, ) -> Message:
        return self.bot.send_message(
            chat_id=tg_user_id,
            text=constants.USER_DECLINED_SHARE_PROPOSAL.format(DECLINER_TG_NAME=decliner_tg_name),
        )

    """
    def user_accepted_share_proposal(self, ) -> Message:
        No need base accept cuz message is differ for all (unlike for decline)
    """

    @log
    def user_declined_request_proposal(self, tg_user_id: int, decliner_tg_name: str, ) -> Message:
        return self.bot.send_message(
            chat_id=tg_user_id,
            text=constants.USER_DECLINED_REQUEST_PROPOSAL.format(DECLINER_TG_NAME=decliner_tg_name),
        )

    @log
    def remove_proposal_message(self, message_id_to_delete: int, ) -> bool:
        return self.bot.delete_message(chat_id=self.tg_user_id, message_id=message_id_to_delete, )

    @log
    def internal_error(self, ) -> Message:
        return self.bot.send_message(chat_id=self.tg_user_id, text=constants.INTERNAL_ERROR, )

    class Deprecated:  # pragma: no cover
        """Not in use"""

        def __init__(self, user: User, bot: Bot | ExtBot, ):
            # Bot is indeed the same for all instances, but can't be a class attribute because not exists yet
            self.bot = bot
            self.tg_user_id = user.tg_user_id
            self.tg_name = user.tg_name

        @log
        def no_more_posts(self, ) -> Message:
            return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Deprecated.NO_MORE_POSTS, )

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
from pprint import pformat as pprint_pformat
from typing import TYPE_CHECKING
import traceback

# noinspection PyPackageRequirements
from telegram import Update
# noinspection PyPackageRequirements
from telegram.ext import ConversationHandler
# noinspection PyPackageRequirements
from telegram.error import (BadRequest as tg_error_BadRequest, Unauthorized as tg_error_Unauthorized, )

import app.exceptions
import app.generation
# This classes need, not only for type checking
import app.models.mix
import app.tg.ptb.config
import app.tg.ptb.utils

from app.tg.ptb import services

if TYPE_CHECKING:
    from custom_ptb.callback_context import CustomCallbackContext as CallbackContext


class GetStatisticWith:

    @staticmethod
    def entry_point(_: Update, context: CallbackContext, ):
        context.user_data.view.cjm.say_statistic_hello()
        return 0

    @staticmethod
    def entry_point_handler(update: Update, context: CallbackContext, ):
        # TODO show profile instead of fullname
        with_tg_user_id = app.tg.ptb.utils.accept_user(message=update.message)
        if with_tg_user_id is None:
            context.user_data.view.warn.incorrect_user()
            return
        match_stats = app.models.mix.MatchStats(
            user=context.user_data.current_user,
            with_tg_user_id=with_tg_user_id,
        )
        try:
            context.user_data.view.cjm.show_statistic(match_stats=match_stats, )
        except (tg_error_Unauthorized, tg_error_BadRequest):
            context.user_data.view.user_not_found()
            return
        return app.tg.ptb.utils.end_conversation()


def faq(_: Update, context: CallbackContext, ):
    context.user_data.view.cjm.faq()


def all_bot_commands_handler(_: Update, context: CallbackContext, ):
    context.user_data.view.cjm.show_bot_commands()


def personal_example(_: Update, context: CallbackContext, ):
    user = context.user_data.current_user
    # May be improved with "app.models.mix.MatchStats.get_random.statistic" classmethod
    statistic = app.models.mix.MatchStats(user=user, with_tg_user_id=123456, set_statistic=False, )
    statistic.fill_random()
    context.user_data.view.cjm.show_statistic(match_stats=statistic, )


def auto_deb_logger(update: Update, context: CallbackContext, ):
    if app.tg.ptb.config.Config.is_log is True:
        log_data = {
            "message_text": update.effective_message.text,
            "message_attachment": update.effective_message.effective_attachment,
            "callback_data": getattr(update.callback_query, 'data', None),
            "user_data": context.user_data,
            "chat_data": context.chat_data,
            "bot_data": context.bot_data,
        }
        app.tg.ptb.config.Config.logger.debug('\n' + pprint_pformat({k: v for k, v in log_data.items() if v}))


def log_call_stack_handler(_: Update, __: CallbackContext, ):
    ...


def gen_bots_handler_cmd(update: Update, context: CallbackContext, ):
    try:
        num = app.utils.get_num_from_text(text=update.effective_message.text)
    except ValueError:  # invalid literal for int() with base 10: '' (if no digits in message)
        context.user_data.view.warn.nan_help_msg()
        return
    num_to_gen = app.utils.limit_num(num=num, min_num=1, max_num=99, )
    services.System.gen_bots(bots_ids=list(range(num_to_gen)), )
    context.user_data.view.say_ok()


def gen_me_handler_cmd(update: Update, context: CallbackContext, ):
    services.System.gen_bots(bots_ids=[update.effective_user.id, ], gen_votes=True, )
    default_personal_collections = services.Collection.get_defaults(
        prefix=services.Collection.NamePrefix.PERSONAL.value,
    )
    for collection in default_personal_collections:  # Set votes for default posts
        for post in collection.posts:
            context.user_data.current_user.set_vote(
                vote=services.System.generator.gen_vote(user=context.user_data.current_user, post=post, ),
                post=post,
            )
    context.user_data.view.say_ok()


def log_update_handler(update: Update, _: CallbackContext, ) -> None:
    if update.effective_message.effective_attachment:
        if isinstance(update.effective_message.effective_attachment, list):  # If photo (photo always is list)
            type_ = type(update.effective_message.effective_attachment[0]).__name__
        else:
            type_ = type(update.effective_message.effective_attachment).__name__
        content = f'''{type_}:{update.effective_message.caption or '""'}'''  # '""' - to explicit show empty line
    else:
        content = f'Text:{update.effective_message.text}'
    app.tg.ptb.config.Config.view_logger.debug(f'{update.effective_user.id}:{content}')


def error_handler(_: Update, context: CallbackContext, ) -> None:
    """
    Log the error and send a telegram message to notify the developer.
    The error won’t show up in the logger, so you need to reraise the error for that.
    """
    if isinstance(context.error, app.exceptions.KnownException) is False:
        app.tg.ptb.config.Config.logger.error(msg=traceback.format_exc())


def unclickable_cbk_handler(update: Update, context: CallbackContext, ):
    context.user_data.view.unclickable_button(tooltip=update.callback_query, )


def cancel(_: Update, context: CallbackContext, ):  # Common handler for all conversations to cancel them
    context.user_data.view.cancel()
    return ConversationHandler.END

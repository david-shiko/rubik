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

import app.tg.ptb.utils
import app.tg.ptb.constants
import app.tg.ptb.config
from app.tg.ptb.classes.posts import ChannelPublicPost, BotPublicPost, PersonalPost
import app.tg.ptb.classes.collections
import app.tg.ptb.services

if TYPE_CHECKING:
    from custom_ptb.callback_context import CustomCallbackContext as CallbackContext
    # noinspection PyPackageRequirements
    from telegram import Update, CallbackQuery
    import app.structures.base


def accept_user_handler(update: Update, context: CallbackContext, ) -> None | int:
    recipient_tg_user_id = app.tg.ptb.utils.accept_user(message=update.message)  # str tg_user_id or contact
    if recipient_tg_user_id is None:
        context.user_data.view.warn.incorrect_user()
        return None
    return recipient_tg_user_id


def check_correct_continue(update: Update, context: CallbackContext, ) -> bool:
    if update.message.text.lower().strip() != app.tg.ptb.constants.Shared.Words.FINISH.lower():
        context.user_data.view.warn.incorrect_finish()
        return False
    return True


def check_is_collections_chosen(context: CallbackContext, ) -> bool:
    if not context.user_data.tmp_data.collections_id_to_share:
        context.user_data.view.collections.collections_to_share_not_chosen()
        return False
    return True


def check_reg(  # Not in use
        context: CallbackContext,
        action: app.structures.base.ReqRequiredActions,
        tooltip: CallbackQuery = None,
        raise_: bool = True,
) -> bool | None:
    is_registered = context.user_data.current_user.is_registered
    if is_registered is False:
        context.user_data.view.reg_required(action=action, tooltip=tooltip, )
        if raise_ is True:
            raise app.exceptions.ReqRequired
    return is_registered


def callback_to_post(
        update: Update,
        context: CallbackContext,
) -> ChannelPublicPost | BotPublicPost | PersonalPost | None:
    # Delete post / post buttons on error?
    # Dirty, better to bind cbk and cls
    if app.tg.ptb.config.CHANNEL_PUBLIC_VOTE_CBK_S in update.callback_query.data:
        post_cls = app.tg.ptb.classes.posts.ChannelPublicPost
    elif app.tg.ptb.config.PUBLIC_VOTE_CBK_S in update.callback_query.data:
        post_cls = app.tg.ptb.classes.posts.BotPublicPost  # BotPublicPost or PublicPost
    elif app.tg.ptb.config.PERSONAL_VOTE_CBK_S in update.callback_query.data:
        post_cls = app.tg.ptb.classes.posts.PersonalPost
    else:
        raise app.exceptions.UnknownPostType
    try:
        return post_cls.callback_to_post(
            callback=update.callback_query,  # Read vote inside
            connection=context.user_data.current_user.connection,
        )
    except app.exceptions.PostNotFound as e:
        context.user_data.view.posts.post_to_vote_not_found(tooltip=update.callback_query, )
        app.tg.ptb.config.Config.logger.error(e, )
    return None

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
from telegram import Update

import app.tg.ptb.config
import app.exceptions

import app.tg.ptb.actions
import app.tg.ptb.classes.posts
import app.tg.ptb.classes.votes

from app.tg.ptb import services

if TYPE_CHECKING:
    from custom_ptb.callback_context import CustomCallbackContext as CallbackContext


def public_vote_cbk_handler(update: Update, context: CallbackContext, ):
    """
    Callback may be abused, remember this!
    If user pressed button from forwarded message (default disable):
    https://stackoverflow.com/q/46756643/11277611
    """
    vote = app.tg.ptb.classes.votes.PublicVote.callback_to_vote(
        user=context.user_data.current_user,
        callback=update.callback_query,
    )
    try:
        post = app.tg.ptb.actions.callback_to_post(update=update, context=context, )  # Will raise if not found
    except (Exception, app.exceptions.UnknownPostType,) as e:
        app.tg.ptb.config.Config.logger.error(e)
        context.user_data.view.posts.voting_internal_error(tooltip=update.callback_query, )
        return
    if context.user_data.current_user.set_vote(post=post, vote=vote, ) is True:
        """Counting votes in keyboard was disabled (tmp or persistence)"""
        # Update public votes
        # context.dispatcher.run_async(func=services.System.BotPublicPost.mass_update_keyboard_job, bot_post=post, )
        post.update_poll_keyboard(clicker_vote=vote, )
    update.callback_query.answer()


def channel_public_vote_cbk_handler(update: Update, context: CallbackContext, ):  # For voting in the channel
    """
    Callback may be abused, remember this!
    If user pressed button from forwarded message (default disable):
    https://stackoverflow.com/q/46756643/11277611
    """
    vote = app.tg.ptb.classes.votes.PublicVote.callback_to_vote(
        user=context.user_data.current_user,
        callback=update.callback_query,
    )
    try:
        post = app.tg.ptb.actions.callback_to_post(update=update, context=context, )  # Will raise if not found
    except (Exception, app.exceptions.UnknownPostType,) as e:
        app.tg.ptb.config.Config.logger.error(e)
        context.user_data.view.posts.voting_internal_error(tooltip=update.callback_query, )
    else:  # If no exception was raised
        if context.user_data.current_user.set_vote(post=post, vote=vote, ) is True:
            # just post.message_id - is store channel message_id
            post.update_poll_keyboard(message_id=update.callback_query.message.message_id, )
    finally:  # Execute anyway (no matter was or not error)
        update.callback_query.answer()


def personal_vote_cbk_handler(update: Update, context: CallbackContext, ):
    _, str_opposite_tg_user_id, post_id = update.callback_query.data.split()
    clicker_vote = app.tg.ptb.classes.votes.PersonalVote.callback_to_vote(  # TODO rename and move extraction to posts
        user=context.user_data.current_user,
        callback=update.callback_query,
    )
    try:
        # TODO add method to get 2 voted users
        post = app.tg.ptb.actions.callback_to_post(update=update, context=context, )  # Will raise if not found
    except (Exception, app.exceptions.UnknownPostType,) as e:
        app.tg.ptb.config.Config.logger.error(e)
        context.user_data.view.posts.voting_internal_error(tooltip=update.callback_query, )
        return
    else:  # If no exception
        # Save vote before to read the opposite vote (because opposite vote may be yourself vote)
        if context.user_data.current_user.set_vote(vote=clicker_vote, post=post, ) is True:
            post.update_poll_keyboard(
                clicker_vote=clicker_vote,
                opposite_vote=app.tg.ptb.classes.votes.PersonalVote.Mapper.User(
                    tg_user_id=int(str_opposite_tg_user_id),
                ).get_vote(post=post, ),
            )
    finally:  # Execute anyway (no matter was or not error)
        update.callback_query.answer()

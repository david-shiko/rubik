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
# noinspection PyUnresolvedReferences
from pprint import pprint

# noinspection PyPackageRequirements
from telegram import Update
# noinspection PyPackageRequirements
from telegram.error import (BadRequest as tg_error_BadRequest, Unauthorized as tg_error_Unauthorized, )

from app.postconfig import logger

import app.models.posts
import app.models.mix

import app.tg.ptb.actions
import app.tg.ptb.config
import app.tg.ptb.utils
import app.tg.ptb.classes.posts
import app.tg.ptb.classes.collections

from app.tg.ptb import services, constants

import app.tg.ptb.forms.post

if TYPE_CHECKING:
    from custom_ptb.callback_context import CustomCallbackContext as CallbackContext


class CreatePublicPost:

    SEND_KEYWORD = constants.Shared.Words.SEND.lower()

    @staticmethod
    def entry_point(_: Update, context: CallbackContext, ):
        context.user_data.view.posts.say_public_post_hello()
        return 0

    @staticmethod
    def sample_handler(update: Update, context: CallbackContext, ):
        """
        telegram has bot.send_media_group method to send message with multiple attachments,
        but documents and audios can't be mixed with another type of attachments.
        So I'm just sending multiple messages one by one.
        """
        context.user_data.forms.post = app.tg.ptb.forms.post.PublicPost(
            author=context.user_data.current_user,
            message_id=update.message.message_id,
        )
        context.user_data.view.posts.here_post_preview()
        context.user_data.view.posts.show_post(post=context.user_data.forms.post, )
        return 1

    @classmethod
    def confirm_handler(cls, update: Update, context: CallbackContext, ):
        if update.message.text.lower().strip() == cls.SEND_KEYWORD.lower():
            created_post = context.user_data.forms.post.create()
            context.user_data.view.posts.say_success_post()
        else:
            context.user_data.view.warn.incorrect_send()
            return
        # Quickfix to create public votes for bots
        services.System.set_bots_votes_to_post(post=created_post, )
        context.user_data.forms.post = None  # Clear form
        return app.tg.ptb.utils.end_conversation()


class CreatePersonalPost:

    READY_KEYWORD = constants.Shared.Words.READY.lower()
    SKIP_KEYWORD = constants.Shared.Words.SKIP.lower()
    FINISH_KEYWORD = constants.Shared.Words.FINISH.lower()

    @staticmethod
    def entry_point(_: Update, context: CallbackContext, ):
        context.user_data.view.posts.say_personal_post_hello()
        return 0

    @staticmethod
    def entry_point_handler(update: Update, context: CallbackContext, ):
        context.user_data.forms.post = app.tg.ptb.forms.post.PersonalPost(
            author=context.user_data.current_user,
            message_id=update.message.message_id,
        )
        context.user_data.view.posts.show_post(post=context.user_data.forms.post, )
        context.user_data.view.notify_ready_keyword()
        return 1

    @classmethod
    def sample_handler(cls, update: Update, context: CallbackContext, ):
        if update.message.text.lower().strip() != cls.READY_KEYWORD:
            context.user_data.view.warn.incorrect_continue(keyword=cls.READY_KEYWORD, )
            return
        # Read user already created collection
        collection_names_from_db = {collection.name for collection in context.user_data.current_user.get_collections()}
        collection_names = collection_names_from_db or context.user_data.forms.post.collection_names  # or default
        context.user_data.view.collections.ask_collection_for_post(collection_names=collection_names, )
        return 2

    @classmethod
    def collections_handler(cls, update: Update, context: CallbackContext, ):
        """
        telegram has bot.send_media_group method to send message with multiple attachments,
        but documents and audios can't be mixed with another type of attachments.
        So I'm just sending multiple messages one by one.
        """
        text = update.message.text.strip()
        if text.lower() != cls.SKIP_KEYWORD:
            context.user_data.forms.post.handle_collection_names(text=text, )
        context.user_data.view.collections.show_chosen_collections_for_post(
            collection_names=context.user_data.forms.post.collection_names,
        )
        return 3

    @classmethod
    def confirm_handler(cls, update: Update, context: CallbackContext, ):
        if update.message.text.lower().strip() != cls.FINISH_KEYWORD:
            context.user_data.view.warn.incorrect_finish()
            return
        context.user_data.forms.post.create()
        context.user_data.view.posts.say_success_post()
        return app.tg.ptb.utils.end_conversation()


def public_post_mass_sending_handler(_: Update, context: CallbackContext, ):
    if public_post := app.tg.ptb.classes.posts.PublicPost.read_mass():  # Move to service ?
        context.dispatcher.run_async(func=public_post.mass_sending_job)
        context.user_data.view.say_ok()
    else:
        context.user_data.view.posts.no_mass_posts()


def public_post_in_channel_handler(_: Update, context: CallbackContext, ):
    if post := app.tg.ptb.classes.posts.ChannelPublicPost.read_mass():  # Move to service ?
        post.show(recipient=post.POSTS_CHANNEL_ID, )
        context.user_data.view.say_ok()
    else:
        context.user_data.view.posts.no_mass_posts()


def get_pending_public_posts_handler(_: Update, context: CallbackContext, ):  # Set limit
    if pending_posts := services.PublicPost.get_pending_posts(
            connection=context.user_data.current_user.connection,
    ):
        context.user_data.view.posts.show_pendings(posts=pending_posts, )
    else:
        context.user_data.view.posts.no_pending_posts()


def update_public_post_status_cbk(update: Update, context: CallbackContext, ):
    _, str_post_id, str_new_status = update.callback_query.data.split()
    post = app.tg.ptb.classes.posts.PublicPost.read(
        post_id=int(str_post_id),
        connection=context.user_data.current_user.connection,
    )
    post.update_status(status=post.Status(int(str_new_status)))
    context.user_data.view.say_ok()
    return update.callback_query.answer()


def get_public_post(_: Update, context: CallbackContext, ):
    # TODO Put user in queue if not posts
    # TODO save in cache is mass posts exists
    if public_post := context.user_data.current_user.get_new_public_post():
        old_vote = context.user_data.current_user.get_vote(post=public_post, )
        public_post.remove_old_user_post(tg_user_id=old_vote.user.tg_user_id, message_id=old_vote.message_id, )
        sent_message = context.user_data.view.posts.show_post(post=public_post, )
        context.user_data.current_user.upsert_shown_post(
            new_message_id=sent_message.message_id,
            public_post=public_post,
        )
    elif context.user_data.current_user.matcher.is_user_has_covotes:  # Behavior
        context.user_data.view.posts.no_new_posts()  # No new posts for user
    else:
        context.user_data.view.posts.no_mass_posts()


def get_my_personal_posts(_: Update, context: CallbackContext, ):
    # VotedPersonalPost is deprecated ?
    if personal_posts := context.user_data.current_user.get_personal_posts():
        voted_posts = app.tg.ptb.classes.posts.VotedPersonalPost.convert(
            posts=personal_posts,
            clicker=context.user_data.current_user,
            opposite=context.user_data.current_user,
        )
        context.user_data.view.posts.here_your_personal_posts()
        context.user_data.view.posts.show_posts(posts=voted_posts)
    else:
        context.user_data.view.posts.no_personal_posts()


def get_my_collections_handler_cmd(_: Update, context: CallbackContext, ):
    """Return keyboard with personal collection names"""
    if collections := context.user_data.current_user.get_collections():
        context.user_data.view.collections.show_my_collections(collections=collections, )
    else:
        context.user_data.view.collections.no_collections()


class SharePersonalPosts:
    @staticmethod
    def entry_point(_: Update, context: CallbackContext, ):
        # User personal posts may be cached
        if context.user_data.current_user.get_personal_posts():
            context.user_data.view.posts.ask_who_to_share_personal_posts()
            return 0
        else:
            context.user_data.view.posts.no_personal_posts()
            return app.tg.ptb.utils.end_conversation()

    @staticmethod
    def recipient_handler(update: Update, context: CallbackContext, ):
        recipient_tg_user_id = app.tg.ptb.utils.accept_user(
            message=update.effective_message,  # str tg_user_id or contact
        )
        if recipient_tg_user_id is not None:
            try:
                # TODO pass tg_name
                context.user_data.view.posts.ask_accept_personal_posts(recipient_tg_user_id=recipient_tg_user_id, )
                context.user_data.view.posts.say_user_got_share_proposal(recipient_tg_user_id=recipient_tg_user_id, )
            except (tg_error_Unauthorized, tg_error_BadRequest,):
                context.user_data.view.user_not_found()
                return
        else:
            context.user_data.view.warn.incorrect_user()
            return
        return app.tg.ptb.utils.end_conversation()


class RequestPersonalPosts:
    @staticmethod
    def entry_point(_: Update, context: CallbackContext, ):
        context.user_data.view.posts.ask_who_to_request_personal_posts()
        return 0

    @staticmethod
    def recipient_handler(update: Update, context: CallbackContext, ):
        recipient_tg_user_id = app.tg.ptb.utils.accept_user(message=update.message, )
        if recipient_tg_user_id is not None:
            try:
                # TODO pass tg_name
                context.user_data.view.posts.ask_permission_to_share_personal_posts(
                    recipient_tg_user_id=recipient_tg_user_id,
                )
                context.user_data.view.posts.say_user_got_request_proposal(
                    recipient_tg_user_id=recipient_tg_user_id
                )
            except (tg_error_Unauthorized, tg_error_BadRequest):
                context.user_data.view.user_not_found()
                return
        else:
            context.user_data.view.warn.incorrect_user()
            return
        return app.tg.ptb.utils.end_conversation()


def share_personal_posts_cbk_handler(update: Update, context: CallbackContext, ) -> bool:
    posts_sender, flag = app.tg.ptb.classes.posts.PersonalPost.extract_cbk_data(
        callback_data=update.callback_query.data,
    )
    if flag:
        context.user_data.view.posts.user_accepted_share_proposal(
            accepter_tg_name=context.user_data.current_user.tg_name,
        )
        posts_sender.share_personal_posts(recipient=context.user_data.current_user)
    else:
        context.user_data.view.posts.user_declined_share_proposal(
            posts_sender_tg_user_id=posts_sender.tg_user_id,
        )
    context.user_data.view.cjm.remove_sharing_button(message=update.effective_message, )
    return update.callback_query.answer()


def request_personal_post_cbk_handler(update: Update, context: CallbackContext, ):
    try:
        posts_recipient, flag = app.tg.ptb.classes.posts.PersonalPost.extract_cbk_data(
            callback_data=update.callback_query.data,
        )
        if not flag:
            context.user_data.view.posts.user_declined_request_proposal(
                posts_recipient_tg_user_id=posts_recipient.tg_user_id,
            )
            return
        context.user_data.view.posts.user_accepted_request_proposal(
            posts_recipient_tg_user_id=posts_recipient.tg_user_id,
        )
        is_shared_success = context.user_data.current_user.share_personal_posts(recipient=posts_recipient, )
        if is_shared_success is False:
            context.user_data.view.posts.no_personal_posts()  # Notify user itself
            context.user_data.view.posts.sender_has_no_personal_posts(recipient_tg_user_id=posts_recipient.tg_user_id, )
    except Exception as e:
        logger.error(e)
        context.user_data.view.internal_error()
    finally:
        context.user_data.view.cjm.remove_sharing_button(message=update.effective_message, )
        update.callback_query.answer()

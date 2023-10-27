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
# noinspection PyPackageRequirements
from telegram.error import (BadRequest as tg_error_BadRequest, Unauthorized as tg_error_Unauthorized, )

from app.tg.ptb.classes.collections import Collection
from app.tg.ptb import services, actions, utils, constants

if TYPE_CHECKING:
    from custom_ptb.callback_context import CustomCallbackContext as CallbackContext


class SharePersonalCollections:

    @staticmethod
    def entry_point(_: Update, context: CallbackContext, ):
        # User personal collections may be cached
        if collections := context.user_data.current_user.get_collections(cache=True, ):
            services.Collection.Keyboards.set(
                collections=collections,
                keyboard=Collection.Keyboards.Mark,
            )
            context.user_data.view.collections.show_collections(
                collections=collections,
                text=constants.Collections.ASK_TO_SHARE,
            )
            context.user_data.view.notify_ready_keyword()
            return 0
        else:
            context.user_data.view.collections.no_collections()
            return utils.end_conversation()

    @staticmethod
    def mark_to_share_cbk_handler(update: Update, context: CallbackContext, ):
        """Mark collections to be shared"""
        collection_id = Collection.Keyboards.Mark.extract_cbk_data(cbk_data=update.callback_query.data, )
        context.user_data.tmp_data.collections_id_to_share.add(collection_id)  # TODO  remove tmp data
        update.callback_query.answer()

    @staticmethod
    def continue_handler(update: Update, context: CallbackContext, ):
        """Check is user finished to choose collections to share"""
        if not actions.check_correct_continue(update=update, context=context, ):
            return
        elif not actions.check_is_collections_chosen(context=context, ):
            return
        context.user_data.view.collections.ask_who_to_share()
        return 1

    @staticmethod
    def recipient_handler(update: Update, context: CallbackContext, ):
        """Get correct recipient from user"""
        recipient_tg_user_id = actions.accept_user_handler(update=update, context=context, )
        if recipient_tg_user_id is None:
            return
        try:
            context.user_data.view.collections.ask_accept_collections(
                recipient_tg_user_id=recipient_tg_user_id,
                collections_ids=context.user_data.tmp_data.collections_id_to_share,
            )
        except (tg_error_Unauthorized, tg_error_BadRequest,):
            context.user_data.view.user_not_found()
            return
        context.user_data.view.posts.say_user_got_share_proposal(recipient_tg_user_id=recipient_tg_user_id, )
        return utils.end_conversation()

    @staticmethod
    def recipient_decision_cbk_handler(update: Update, context: CallbackContext, ):
        """
        cbk handling accessible anytime
        - - -
        Not a part of this CH but logically related.
        A small difference with app.tg.ptb.handlers.start.accept_collections_cbk_handler
        because here (logically) only sender collections (for now), there any collections (including defaults).
        """
        try:
            _, str_sender_tg_user_id, str_flag, *str_collections_id = update.callback_query.data.split()
            if bool(int(str_flag)) is False:  # If declined
                context.user_data.view.collections.recipient_declined_share_proposal(
                    sender_tg_user_id=int(str_sender_tg_user_id),
                )
                return
            # Got collections ids may contain not only sender collections but a default too
            collections = services.Collection.get_by_ids(
                ids=[int(str_collection_id) for str_collection_id in str_collections_id],
                user=context.user_data.current_user,
            )
            if not collections:
                context.user_data.view.collections.shared_collections_not_found()
                return
            context.user_data.view.collections.show_collections_to_recipient(
                sender_tg_user_id=int(str_sender_tg_user_id),
                collections=collections,  # Create user.read_marked_collections method?
            )
            context.user_data.view.collections.recipient_accepted_share_proposal(
                sender_tg_user_id=int(str_sender_tg_user_id),  # Need name rather than id, but ok
            )
        finally:
            context.user_data.view.cjm.remove_sharing_button(message=update.effective_message, )
            update.callback_query.answer()

    @staticmethod
    def show_collection_posts_to_recipient_cbk_handler(update: Update, context: CallbackContext, ):
        """
        cbk handling accessible anytime
        Not a part of this CH but logically related.
        """
        sender, collection_id = Collection.Keyboards.ShowPostsForRecipient.extract_cbk_data(
            cbk_data=update.callback_query.data,
            user=context.user_data.current_user,
        )
        unprepared_posts = Collection.get_posts(  # No matter tg or logic cls
            collection_id=collection_id,
            connection=context.user_data.current_user.connection,
        )
        prepared_posts = services.Post.prepare_for_send(
            posts=unprepared_posts,
            clicker=context.user_data.current_user,  # In global scenario tg_user_id is equal (but not the obj)
            opposite=sender,  # In global scenario tg_user_id is equal (but not the obj)
        )
        context.user_data.view.collections.show_collection_posts(posts=prepared_posts, )
        update.callback_query.answer()

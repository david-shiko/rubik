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

from app.tg.ptb import keyboards, services, constants
from app.tg.ptb.views.base import log, Base, Shared
from app.tg.ptb.classes import posts as ptb_posts

if TYPE_CHECKING:
    # noinspection PyPackageRequirements
    from telegram import Message, MessageId, CallbackQuery
    from app.structures import type_hints


class Posts(Base):
    def __init__(self, shared_view: Shared, *args, **kwargs):
        super().__init__(*args, **kwargs, )
        self.shared_view = shared_view

    @log
    def delete_post(self, message_id: int, tg_user_id: int | None = None, ) -> bool:
        return self.bot.delete_message(chat_id=tg_user_id or self.tg_user_id, message_id=message_id, )

    @log
    def no_mass_posts(self, ) -> Message:
        return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Posts.Public.NO_MASS_POSTS, )

    def show_pending(self, post: ptb_posts.PublicPostInterface, ) -> MessageId:
        return self.bot.copy_message(
            chat_id=self.tg_user_id,
            from_chat_id=post.STORE_CHANNEL_ID,
            message_id=post.message_id,
            reply_markup=post.Keyboards.ShowPending.update_status(post=post, )
        )

    def show_pendings(self, posts: list[ptb_posts.PublicPost], ) -> list[MessageId]:
        result = []
        for post in posts:
            result.append(self.show_pending(post=post, ))
        return result

    @log
    def no_new_posts(self, ) -> Message:
        return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Posts.Public.NO_NEW_POSTS, )

    @log
    def no_pending_posts(self, ) -> Message:
        return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Posts.Public.NO_PENDING, )

    @log
    def no_personal_posts(self, ) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.Posts.Personal.NO_POSTS,
            reply_markup=keyboards.create_personal_post,
        )

    @log
    def sender_has_no_personal_posts(self, recipient_tg_user_id: int, ) -> Message:
        return self.bot.send_message(
            chat_id=recipient_tg_user_id,
            text=constants.Posts.Personal.SENDER_HAS_NO_POSTS,
        )

    @log
    def say_user_got_share_proposal(self, recipient_tg_user_id: int, ) -> Message:
        return self.shared_view.say_user_got_share_proposal(recipient_tg_user_id=recipient_tg_user_id, )

    @log
    def say_user_got_request_proposal(self, recipient_tg_user_id: int, ) -> Message:
        return self.shared_view.say_user_got_request_proposal(recipient_tg_user_id=recipient_tg_user_id, )

    @log
    def user_declined_share_proposal(self, posts_sender_tg_user_id: int, ) -> Message:
        return self.shared_view.user_declined_share_proposal(
            tg_user_id=posts_sender_tg_user_id,
            decliner_tg_name=self.tg_name,
        )

    @log
    def user_declined_request_proposal(self, posts_recipient_tg_user_id: int, ) -> Message:
        return self.shared_view.user_declined_request_proposal(
            tg_user_id=posts_recipient_tg_user_id,
            decliner_tg_name=self.tg_name,
        )

    @log
    def user_accepted_share_proposal(self, accepter_tg_name: str) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.Posts.Personal.USER_ACCEPTED_SHARE_PROPOSAL.format(ACCEPTER_TG_NAME=accepter_tg_name),
        )

    @log
    def user_accepted_request_proposal(self, posts_recipient_tg_user_id: int, ) -> Message:
        return self.bot.send_message(
            chat_id=posts_recipient_tg_user_id,
            text=constants.Posts.Personal.USER_ACCEPTED_REQUEST_PROPOSAL.format(ACCEPTER_TG_NAME=self.tg_name),
        )

    @log
    def post_not_found(self, ) -> Message:
        return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Posts.NOT_FOUND, )

    @log
    def post_to_vote_not_found(self, tooltip: CallbackQuery, ) -> Message | bool:
        return tooltip.answer(text=constants.Posts.POST_TO_VOTE_NOT_FOUND, show_alert=True, )

    @staticmethod
    @log
    def voting_internal_error(tooltip: CallbackQuery, ) -> Message | bool:
        return tooltip.answer(text=constants.INTERNAL_ERROR, show_alert=True, )

    @log
    def cant_send_posts_to_user_help_text(self, posts_recipient_tg_user_id: int | None = None, ) -> Message:
        """  # Not in use"""
        return self.bot.send_message(
            text=constants.Posts.Personal.CANT_SEND_TO_THIS_USER,
            chat_id=posts_recipient_tg_user_id or self.tg_user_id
        )

    @log
    def say_public_post_hello(self, ) -> Message:
        return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Posts.Public.HELLO, )

    @log
    def say_success_post(self, ) -> Message:
        return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Posts.CREATED_SUCCESSFULLY, )

    @log
    def say_personal_post_hello(self, ) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.Posts.Personal.HELLO,
            reply_markup=keyboards.cancel,
        )

    @log
    def ask_who_to_share_personal_posts(self, ):
        return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Posts.Personal.WHO_TO_SHARE, )

    @log
    def ask_who_to_request_personal_posts(self, ):
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.Posts.Personal.WHO_TO_REQUEST,
            reply_markup=keyboards.remove(),
        )

    @log
    def ask_permission_to_share_personal_posts(self, recipient_tg_user_id: int, ):
        return self.bot.send_message(
            chat_id=recipient_tg_user_id,
            text=constants.Posts.Personal.NOTIFY_REQUEST_PROPOSAL.format(USER_TG_NAME=self.tg_name),
            reply_markup=services.PersonalPost.ask_permission_share_personal_post(
                tg_user_id=self.tg_user_id
            ),
        )

    @log
    def here_your_personal_posts(self, ) -> Message:
        return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Posts.Personal.HERE_YOUR_POSTS, )

    @log
    def ask_accept_personal_posts(self, recipient_tg_user_id: int, ):
        keyboard = services.PersonalPost.get_accept_post_keyboard(sender_tg_user_id=self.tg_user_id, )
        return self.bot.send_message(
            chat_id=recipient_tg_user_id,  # Add button to show profile instead of fullname
            text=constants.Posts.Personal.NOTIFY_SHARE_PROPOSAL.format(USER_TG_NAME=self.tg_name),
            reply_markup=keyboard,
        )

    @staticmethod
    @log
    def show_post(post):
        """Show any post"""
        return post.send()  # TOdo probably will cause error

    @log
    def show_posts(self, posts: list[type_hints.post], ) -> list[Message]:
        result = []
        for post in posts:
            sent_post = self.show_post(post=post, )
            result.append(sent_post)
        return result

    @log
    def here_post_preview(self, ) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=f'{constants.Posts.HERE_POST_PREVIEW}',
            reply_markup=keyboards.send_cancel,
        )

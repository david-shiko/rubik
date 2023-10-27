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

from app.tg.ptb import constants, keyboards, services
from app.tg.ptb.views.base import log, Base
from app.tg.ptb.views.posts import Posts as PostsView, Shared
from app.tg.ptb.classes import collections as ptb_collections

if TYPE_CHECKING:
    # noinspection PyPackageRequirements
    from telegram import Bot, Message
    # noinspection PyPackageRequirements
    from telegram.ext import ExtBot
    from app.structures import type_hints
    from app.tg.ptb.classes.users import User


class Collections(Base, ):
    def __init__(self, bot: Bot | ExtBot, user: User, posts_view: PostsView, shared_view: Shared, ):
        super().__init__(user=user, bot=bot, )
        self.posts_view = posts_view
        self.shared_view = shared_view

    @log
    def show_collections(
            self,
            collections: list[ptb_collections.Collection],
            text: str,
            sender_tg_user_id: int | None = None,  # In case of sharing collections
    ) -> Message:
        sender_tg_user_id = sender_tg_user_id or self.tg_user_id
        sent_message = self.bot.send_message(
            text=text,
            chat_id=self.tg_user_id,
            reply_markup=services.Collection.Keyboards.show_many(
                sender_tg_user_id=sender_tg_user_id,
                collections=collections,
            ), )
        return sent_message

    @log
    def no_collections(self, ) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.Collections.NO_COLLECTIONS,
            reply_markup=keyboards.create_personal_post,
        )

    @log
    def ask_collection_for_post(self, collection_names: list[str], ) -> Message:
        listed_collections = "\n".join(f"{i + 1}. {name}." for i, name in enumerate(collection_names))
        text = (
            f'{constants.Collections.ASK_FOR_NAMES}\n'
            f'{constants.Collections.MAX_NAME_LEN}\n'
            f'{constants.Collections.HERE_YOUR_COLLECTIONS}\n'
            f'{listed_collections}'
        )
        return self.bot.send_message(chat_id=self.tg_user_id, text=text, reply_markup=keyboards.skip_cancel, )

    @log
    def collections_to_share_not_chosen(self, ) -> Message:
        return self.bot.send_message(
            text=constants.Collections.COLLECTIONS_TO_SHARE_NOT_CHOSE,
            chat_id=self.tg_user_id,
            reply_markup=keyboards.finish_cancel,
        )

    @log
    def show_chosen_collections_for_post(
            self,
            collection_names: set[str],
    ) -> Message:
        text = constants.Collections.SAY_CHOSE_FOR_POST
        # collection or coll.name
        str_collection_names = '.\n'.join(collection_names, )
        text = f'{text}\n{str_collection_names}.'  # backslash isn't allowed in fstring brackets
        return self.bot.send_message(chat_id=self.tg_user_id, text=text, reply_markup=keyboards.finish_cancel, )

    @log
    def ask_collection(self, ) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.Collections.ASK_TO_SHARE,
            reply_markup=keyboards.skip_cancel,
        )

    @log
    def ask_who_to_share(self, ) -> Message:
        return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Collections.WHO_TO_SHARE, )

    @log
    def recipient_declined_share_proposal(self, sender_tg_user_id: int, ) -> Message:
        return self.shared_view.user_declined_request_proposal(
            tg_user_id=sender_tg_user_id,
            decliner_tg_name=self.tg_name,
        )

    @log
    def recipient_accepted_share_proposal(self, sender_tg_user_id: int, ) -> Message:
        return self.bot.send_message(
            chat_id=sender_tg_user_id,
            text=constants.Collections.USER_ACCEPTED_SHARE_PROPOSAL.format(ACCEPTER_TG_NAME=self.tg_name, ),
        )

    @log
    def show_collection_posts(self, posts: list[type_hints.post], ) -> None:
        if posts:
            self.here_collection_posts()
            self.posts_view.show_posts(posts=posts, )
        else:
            self.no_posts_in_collection()

    @log
    def no_posts_in_collection(self, ):
        return self.bot.send_message(
            text=constants.Collections.NO_POSTS,
            chat_id=self.tg_user_id,
        )

    @log
    def here_collection_posts(self, ) -> Message:
        return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Collections.HERE_POSTS, )

    @log
    def ask_accept_collections(self, recipient_tg_user_id: int, collections_ids: set[int]):
        return self.bot.send_message(
            chat_id=recipient_tg_user_id,  # Add button to show profile if registered instead of fullname
            text=constants.Collections.NOTIFY_SHARE_PROPOSAL.format(USER_TG_NAME=self.tg_name),
            reply_markup=services.Collection.Keyboards.accept_collections(
                sender_tg_user_id=self.tg_user_id,
                collections_ids=collections_ids,
            )
        )

    def show_collections_to_recipient(
            self,
            collections: list[ptb_collections.Collection],
            sender_tg_user_id: int | None = None,  # In case of sharing collections
    ) -> Message:
        services.Collection.Keyboards.set(
            collections=collections,
            # False positive mypy warning, it's considering passed keyboard as abstract and not concrete implementation
            keyboard=services.Collection.Mapper.Model.Keyboards.ShowPostsForRecipient,  # type: ignore[type-abstract]
        )
        return self.show_collections(
            collections=collections,
            sender_tg_user_id=sender_tg_user_id,
            text=constants.Collections.HERE_SHARED,
        )

    def show_my_collections(self, collections: list[ptb_collections.Collection], ) -> Message:
        services.Collection.Keyboards.set(
            collections=collections,
            # False positive mypy warning, it's considering passed keyboard as abstract and not concrete implementation
            keyboard=services.Collection.Mapper.Model.Keyboards.Show,  # type: ignore[type-abstract]
        )
        return self.show_collections(
            collections=collections,
            text=constants.Collections.HERE_YOUR_COLLECTIONS,
        )

    @log
    def shared_collections_not_found(self, ) -> Message:
        return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Collections.SHARED_COLLECTIONS_NOT_FOUND, )

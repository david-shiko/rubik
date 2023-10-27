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
from enum import Enum
from typing import TYPE_CHECKING, Type, Set, TypeVar
from abc import ABC, abstractmethod
from types import SimpleNamespace

# noinspection PyPackageRequirements
from telegram import InlineKeyboardMarkup as tg_IKM, InlineKeyboardButton as tg_IKB
# noinspection PyPackageRequirements
from telegram.error import Unauthorized, BadRequest

import app.tg.ptb.constants

import app.services
import app.tg.ptb.config
import app.tg.ptb.classes.posts
import app.tg.ptb.classes.collections

if TYPE_CHECKING:
    # noinspection PyPackageRequirements
    from telegram import Message, Update
    from app.structures import type_hints
    import app.tg.ptb.classes.users


class SystemInterface(app.services.SystemInterface, ABC):
    BotPublicPost: Type[BotPublicPostInterface]

    class Mapper(ABC):
        User: app.tg.ptb.classes.users.User
        PublicVote: app.tg.ptb.classes.votes.PublicVote


class _System(app.services.System, SystemInterface, ):
    class Mapper:
        User = app.tg.ptb.classes.users.User
        PublicVote = app.tg.ptb.classes.votes.PublicVote

    BotPublicPost: Type[BotPublicPostInterface]
    user = Mapper.User.from_user(user=app.services.System.user, )


class BotPublicPostInterface(ABC, ):
    System: Type[System]

    @classmethod
    @abstractmethod
    def mass_send_job(cls, bot_post: app.tg.ptb.classes.posts.BotPublicPostInterface, ) -> None:
        ...

    @classmethod
    @abstractmethod
    def mass_update_keyboard_job(cls, bot_post: app.tg.ptb.classes.posts.BotPublicPost, ) -> list[Message]:
        ...

    @classmethod
    @abstractmethod
    def get_voted_users(
            cls,
            post: app.tg.ptb.classes.posts.BotPublicPostInterface,
    ) -> list[app.tg.ptb.classes.users.UserInterface]:
        ...


class _BotPublicPost:
    System: Type[SystemInterface]

    @classmethod
    def mass_send_job(cls, bot_post: app.tg.ptb.classes.posts.BotPublicPostInterface, ) -> None:
        """Send post to group of users (job because most likely usage is inside PTB job (another thread))"""
        # Make separate cursor
        for tg_user_id in cls.System.read_all_users_ids():
            try:
                sent_message = bot_post.send(recipient=tg_user_id, )
            except (Unauthorized, BadRequest):
                continue  # Delete?
            vote_raw = cls.System.Mapper.PublicVote.CRUD.read(  # Crud for reading raw vote
                post_id=bot_post.post_id,
                tg_user_id=tg_user_id,
                connection=cls.System.user.connection,
            )
            bot_post.remove_old_user_post(tg_user_id=tg_user_id, message_id=vote_raw['message_id'], )
            cls.System.Mapper.PublicVote.CRUD.upsert_message_id(
                tg_user_id=tg_user_id,
                post_id=bot_post.post_id,
                new_message_id=sent_message.message_id,
                connection=cls.System.user.connection,
            )
            app.tg.ptb.config.Config.sleep_function(1)

    @classmethod
    def mass_update_keyboard_job(
            cls,
            bot_post: app.tg.ptb.classes.posts.BotPublicPostInterface,
    ) -> list[Message]:  # Message or MessageId
        """Mass update keyboard for users if some vote was set/changed"""
        result = []

        for user in cls.get_voted_users(post=bot_post, ):  # Only voted users have a views to update
            vote = cls.System.Mapper.PublicVote.read(post_id=bot_post.post_id, user=user, )
            try:
                sent_message = bot_post.update_poll_keyboard(clicker_vote=vote, )
            except (Unauthorized, BadRequest):
                continue  # Do nothing if user not exists (no need to delete, he may come back)
            result.append(sent_message)
            app.tg.ptb.config.Config.sleep_function(1)
        return result

    @classmethod
    def get_voted_users(
            cls,
            post: app.tg.ptb.classes.posts.BotPublicPostInterface,
    ) -> list[app.tg.ptb.classes.users.UserInterface]:
        return post.get_voted_users(connection=cls.System.user.connection, )


class BotPublicPost(_BotPublicPost, BotPublicPostInterface, ):
    ...


class System(_System):
    ...


System.BotPublicPost = BotPublicPost
BotPublicPost.System = System


class User(app.tg.ptb.classes.users.User):
    class Mapper:
        User = app.tg.ptb.classes.users.User

    @classmethod
    def create_from_update(cls, update: Update, ) -> app.tg.ptb.classes.users.UserInterface:
        """Used in callback_context ptb func"""
        user = cls.Mapper.User(tg_user_id=update.effective_user.id, )
        return user


class CollectionInterface(app.services.CollectionInterface, ABC, ):
    class Keyboards(ABC):
        ...

        @staticmethod
        @abstractmethod
        def show_many(
                sender_tg_user_id: int,
                collections: list[app.tg.ptb.classes.collections.Collection],
                pattern: str,
                posts_in_row: int = 2
        ) -> tg_IKM:
            ...


class Collection(app.services.Collection, CollectionInterface, ):
    class Mapper:
        Model = app.tg.ptb.classes.collections.Collection

    class Keyboards:
        # Need to bypass False positive Pycharm warning
        T = TypeVar('T', bound=app.tg.ptb.classes.collections.KeyboardInterface, )

        @staticmethod
        def set(
                collections: list[app.tg.ptb.classes.collections.Collection],
                keyboard: Type[T],
        ) -> None:
            """Set the same keyboard for all collections"""
            for collection in collections:
                collection.keyboards.current = keyboard(collection=collection, )

        @staticmethod
        def show_many(
                sender_tg_user_id: int,
                collections: list[app.tg.ptb.classes.collections.Collection],
                posts_in_row: int = 2
        ) -> tg_IKM:
            """
            Provide keyboard with collections names and ids inside the cbk
            """
            keyboard = []
            for index in range(0, len(collections), posts_in_row):  # [1, 2, 3, 4, 5] -> [[1, 2], [3, 4], 5]
                row_buttons = []
                for collection in collections[index: index + posts_in_row]:
                    row_buttons.append(
                        collection.keyboards.current.build_inline_button(
                            sender_tg_user_id=sender_tg_user_id,
                        ), )
                keyboard.append(row_buttons)
            return tg_IKM(inline_keyboard=keyboard, )

        @staticmethod
        def accept_collections(sender_tg_user_id: int, collections_ids: Set[int], ) -> tg_IKM:
            """Not a real Collection responsibility"""
            str_collections_ids = ' '.join([str(collection_id) for collection_id in collections_ids])
            return tg_IKM(
                [[
                    tg_IKB(
                        text=app.tg.ptb.constants.Posts.Personal.Buttons.DECLINE,
                        callback_data=f'{app.tg.ptb.config.ACCEPT_COLLECTIONS_CBK_S} {sender_tg_user_id} 0',
                    ),
                    tg_IKB(
                        text=app.tg.ptb.constants.Posts.Personal.Buttons.ACCEPT,
                        callback_data=(
                            f'{app.tg.ptb.config.ACCEPT_COLLECTIONS_CBK_S} {sender_tg_user_id} 1 {str_collections_ids}'
                        )
                    ),
                ]]
            )


class PublicPost(app.services.PublicPost, ):
    class Mapper:
        PublicPost = app.tg.ptb.classes.posts.PublicPost


class PersonalPost:

    @staticmethod
    def build_accept_post_cbk(sender_tg_user_id: int, flag: int) -> str:
        return f'{app.tg.ptb.config.ACCEPT_PERSONAL_POSTS_CBK_S} {sender_tg_user_id} {flag}'

    @classmethod
    def get_accept_post_keyboard(cls, sender_tg_user_id: int) -> tg_IKM:
        return tg_IKM(
            [[
                tg_IKB(
                    text=app.tg.ptb.constants.Posts.Personal.Buttons.DECLINE,
                    callback_data=cls.build_accept_post_cbk(sender_tg_user_id=sender_tg_user_id, flag=0),
                ),
                tg_IKB(
                    text=app.tg.ptb.constants.Posts.Personal.Buttons.ACCEPT,
                    callback_data=cls.build_accept_post_cbk(sender_tg_user_id=sender_tg_user_id, flag=1),
                ),
            ]]
        )

    @staticmethod
    def ask_permission_share_personal_post(tg_user_id: int, ) -> tg_IKM:
        return tg_IKM(
            [[
                tg_IKB(
                    text=app.tg.ptb.constants.Posts.Personal.Buttons.DISALLOW,
                    callback_data=f'{app.tg.ptb.config.REQUEST_PERSONAL_POSTS_CBK_S} {tg_user_id} 0'
                ),
                tg_IKB(
                    text=app.tg.ptb.constants.Posts.Personal.Buttons.ALLOW,
                    callback_data=f'{app.tg.ptb.config.REQUEST_PERSONAL_POSTS_CBK_S} {tg_user_id} 1'
                ),
            ]]
        )


class PostInterface(ABC, ):
    class Mapper(ABC):
        VotedPersonalPost: app.tg.ptb.classes.posts.VotedPersonalPost
        VotedPublicPost: app.tg.ptb.classes.posts.VotedPublicPost

    @classmethod
    @abstractmethod
    def prepare_for_send(
            cls,
            posts: list[app.tg.ptb.classes.posts.PublicPost | app.tg.ptb.classes.posts.PersonalPost],
            clicker: app.tg.ptb.classes.users.User,
            opposite: app.tg.ptb.classes.users.User,
    ) -> list[app.tg.ptb.classes.posts.PublicPost | app.tg.ptb.classes.posts.VotedPersonalPost]:
        ...


class Post(PostInterface, ):
    class Mapper:
        VotedPersonalPost = app.tg.ptb.classes.posts.VotedPersonalPost
        VotedPublicPost = app.tg.ptb.classes.posts.VotedPublicPost

    @classmethod
    def prepare_for_send(
            cls,
            posts: list[app.tg.ptb.classes.posts.PublicPost | app.tg.ptb.classes.posts.PersonalPost],
            clicker: app.tg.ptb.classes.users.User,
            opposite: app.tg.ptb.classes.users.User,
    ) -> list[app.tg.ptb.classes.posts.VotedPublicPostInterface | app.tg.ptb.classes.posts.VotedPersonalPostInterface]:
        result = []
        for post in posts:
            if isinstance(post, app.tg.ptb.classes.posts.PublicPost):
                prepared_post = cls.Mapper.VotedPublicPost(
                    post=post,
                    clicker_vote=clicker.get_vote(post=post, ),
                )
            elif isinstance(post, app.tg.ptb.classes.posts.PersonalPost):
                prepared_post = cls.Mapper.VotedPersonalPost(
                    post=post,
                    clicker_vote=clicker.get_vote(post=post, ),
                    opposite_vote=opposite.get_vote(post=post, ),
                )
            else:
                raise app.exceptions.UnknownPostType
            result.append(prepared_post)
        return result

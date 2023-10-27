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
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Type

# noinspection PyPackageRequirements
from telegram import InlineKeyboardMarkup as tg_IKM, InlineKeyboardButton as tg_IKB

import app.tg.ptb.config
import app.tg.classes.collections
import app.tg.forms.post
from app.tg.ptb.classes.posts import PublicPost as PtbPublicPost, PersonalPost as PtbPersonalPost
from app.tg.ptb.classes.collections import Collection as PtbCollection

if TYPE_CHECKING:
    # noinspection PyPackageRequirements
    from telegram import MessageId


class PostBase:
    collection_names: set = {app.tg.classes.collections.Collection.DEFAULT_NAME, }


class PublicPostInterface(app.tg.forms.post.PublicPostInterface, ABC, ):
    collection_names: set

    class Mapper:
        PublicPost: Type[PtbPublicPost]

    @abstractmethod
    def create(self, ) -> PublicPostInterface:  # Move to another place or rename to event?
        ...

    @classmethod
    @abstractmethod
    def get_keyboard(cls, ) -> tg_IKM:
        ...

    @abstractmethod
    def send(self, ) -> MessageId:
        ...


class PublicPost(app.tg.forms.post.PublicPost, PostBase, PublicPostInterface, ):

    @dataclass(slots=True, )
    class Mapper:
        PublicPost = PtbPublicPost

    @classmethod
    def get_keyboard(cls, ) -> tg_IKM:
        return tg_IKM(
            [[
                tg_IKB(
                    text=f'{cls.NEG_EMOJI} 0',
                    callback_data=app.tg.ptb.config.EMPTY_CBK_S,  # empty string cbk disallowed
                ),
                tg_IKB(
                    text=f'{cls.POS_EMOJI} 0',
                    callback_data=app.tg.ptb.config.EMPTY_CBK_S,  # empty string cbk disallowed
                ),
            ]]
        )

    def send(self, ) -> MessageId:
        return app.tg.ptb.config.Config.bot.copy_message(
            chat_id=self.author.tg_user_id,
            from_chat_id=self.author.tg_user_id,
            message_id=self.message_id,
            reply_markup=self.get_keyboard(),
        )

    def create(self, ) -> PublicPostInterface:  # Move to another place or rename to event?
        """
        SAve post on TG server and in DB.
        Save post in save place (chat) to prevent illegal post modifying by the author
        """
        sent_message = app.tg.ptb.config.Config.bot.copy_message(
            chat_id=self.STORE_CHANNEL_ID,
            from_chat_id=self.author.tg_user_id,
            message_id=self.message_id,
        )
        self.message_id: int = sent_message.message_id  # Save post in safe chat
        return super().create()  # type: ignore[safe-super]  # False Positive mypy warning without clear reason


class PersonalPostInterface(app.tg.forms.post.PersonalPostInterface, ABC, ):
    collection_names: set

    class Mapper:
        PersonalPost: Type[PtbPersonalPost]
        PtbCollection: Type[PtbCollection]

    @abstractmethod
    def create(self, ) -> PersonalPostInterface:  # Move to another place or rename to event?
        """
        SAve post on TG server and in DB.
        Save post in save place (chat) to prevent illegal post modifying by the author
        """
        ...

    @classmethod
    @abstractmethod
    def get_keyboard(cls, ) -> tg_IKM:  # All posts samples has the same keyboard
        ...

    @abstractmethod
    def send(self) -> MessageId:  # Move to voted post and use "self"?
        ...


class PersonalPost(
    app.tg.forms.post.PersonalPost,
    PostBase,
    PersonalPostInterface,
):

    @dataclass(slots=True, )
    class Mapper:
        PersonalPost = PtbPersonalPost
        Collection = PtbCollection

    def __init__(self, collection_names: set | None = None, *args, **kwargs, ):
        super().__init__(
            collection_names=collection_names or self.collection_names,
            *args,
            **kwargs,
        )

    def create(self, ) -> PersonalPostInterface:  # Move to another place or rename to event?
        """
        SAve post on TG server and in DB.
        Save post in save place (chat) to prevent illegal post modifying by the author
        """
        sent_message = app.tg.ptb.config.Config.bot.copy_message(  # Try forward message rather than copy on fail
            chat_id=self.STORE_CHANNEL_ID,
            from_chat_id=self.author.tg_user_id,
            message_id=self.message_id,
        )
        # noinspection PyAttributeOutsideInit
        self.message_id: int = sent_message.message_id  # Save post in safe chat
        return super().create()  # type: ignore[safe-super]  # False Positive mypy warning without clear reason

    @classmethod
    def get_keyboard(cls, ) -> tg_IKM:  # All posts samples has the same keyboard
        return tg_IKM(
            [[
                tg_IKB(
                    text=cls.DISLIKE,
                    callback_data=app.tg.ptb.config.EMPTY_CBK_S,  # empty string cbk disallowed
                ),
                tg_IKB(
                    text=cls.LIKE,
                    callback_data=app.tg.ptb.config.EMPTY_CBK_S,  # empty string cbk disallowed
                ),
            ]]
        )

    def send(self) -> MessageId:  # Move to voted post and use "self"?
        return app.tg.ptb.config.Config.bot.copy_message(
            chat_id=self.author.tg_user_id,
            from_chat_id=self.author.tg_user_id,
            message_id=self.message_id,
            reply_markup=self.get_keyboard(),
        )

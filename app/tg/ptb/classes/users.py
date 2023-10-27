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
from abc import ABC, abstractmethod

# noinspection PyPackageRequirements
from telegram import (
    InputMediaPhoto as tg_InputMediaPhoto,
    ParseMode as tg_ParseMode,
)
# noinspection PyPackageRequirements
from telegram.error import BadRequest as tg_errors_BadRequest, TimedOut as tg_errors_TimedOut

import app.models.matches
import app.tg.ptb.config
import app.tg.classes.users

if TYPE_CHECKING:
    from psycopg2.extensions import connection as pg_ext_connection
    # noinspection PyPackageRequirements
    from telegram import MessageId, User as telegram_User, Chat as telegram_Chat
    from app.tg.ptb.classes import UserMapper
    import app.tg.ptb.classes.posts
    import app.tg.ptb.classes.collections


class ProfileInterface(app.tg.classes.users.ProfileInterface, ABC, ):
    @abstractmethod
    def prepare_photos_to_send(self, caption: str, ) -> list[tg_InputMediaPhoto]:
        ...

    @abstractmethod
    def send(self, show_to_tg_user_id: int = None, ) -> MessageId:
        ...


# Probably user and new user will need different ptb profile in the future
class Profile(app.tg.classes.users.Profile, ProfileInterface, ):
    DEFAULT_MEDIA_PHOTO = tg_InputMediaPhoto(media=app.config.DEFAULT_PHOTO, parse_mode=tg_ParseMode.HTML, )

    def prepare_photos_to_send(self, caption: str, ) -> list[tg_InputMediaPhoto]:
        photos_to_send = []
        for photo in self.user.photos:
            photos_to_send.append(tg_InputMediaPhoto(media=photo, parse_mode=tg_ParseMode.HTML, ))
        photos_to_send = photos_to_send or [self.DEFAULT_MEDIA_PHOTO]
        photos_to_send[0].caption = caption  # Only first photo need a caption
        return photos_to_send

    def send(self, show_to_tg_user_id: int = None, ) -> MessageId:
        show_to_tg_user_id = show_to_tg_user_id or self.user.tg_user_id
        profile_data = self.get_data()  # Quickfix
        photos_to_send = self.prepare_photos_to_send(caption=profile_data.text, )
        return app.tg.ptb.config.Config.bot.send_media_group(chat_id=show_to_tg_user_id, media=photos_to_send, )


class UserInterface(app.tg.classes.users.UserInterface, ABC, ):
    ...


class User(app.tg.classes.users.User, UserInterface, ):
    """User with methods of telegram"""

    Mapper: UserMapper

    def __init__(
            self,
            tg_user_id: int,
            connection: pg_ext_connection | None = None,
            tg_name: str | None = None,
            fullname: str | None = None,
            goal: app.structures.base.Goal | None = None,
            gender: app.models.users.User.Gender | None = None,
            age: int | None = None,
            country: str | None = None,
            city: str | None = None,
            comment: str | None = None,
            photos: list[str] | None = None,
            is_registered: bool = False,
            is_tg_active: bool = True,
    ):
        super().__init__(
            tg_user_id=tg_user_id,
            connection=connection,
            fullname=fullname,
            goal=goal,
            gender=gender,
            age=age,
            country=country,
            city=city,
            comment=comment,
            photos=photos,
            is_registered=is_registered,
        )
        self.profile: Profile = Profile(user=self, )
        self.tg_name = tg_name
        self._is_tg_active = is_tg_active

    @property
    def is_tg_active(self, ) -> bool:  # Not in use mainly
        try:
            app.tg.ptb.config.Config.bot.get_chat(self.tg_user_id, timeout=2, )  # Very long (time) operation
            self._is_tg_active = True
        except (tg_errors_BadRequest, tg_errors_TimedOut, ):
            self._is_tg_active = False
        return self._is_tg_active

    @is_tg_active.setter
    def is_tg_active(self, value: bool) -> None:
        self._is_tg_active = value

    @property
    def tg_name(self, ) -> str | None:
        return self._tg_name or self.get_my_tg_name()

    @tg_name.setter
    def tg_name(self, value: bool):
        self._tg_name = value

    def share_personal_posts(
            self,
            recipient: app.tg.ptb.classes.users.UserInterface,
            posts: list[app.tg.ptb.classes.posts.PersonalPost] | None = None,
    ) -> bool:
        posts = posts or self.get_personal_posts()
        for post in posts:
            post.share(post_sender=self, post_recipient=recipient, )
        return bool(posts)

    def share_collections_posts(self, recipient: app.tg.ptb.classes.users.UserInterface, ) -> None:
        """Not in use"""
        for collection in self.get_collections():
            self.share_personal_posts(recipient=recipient, posts=collection.posts, )

    @staticmethod
    def get_tg_name(entity: telegram_User | int, timeout: int = 3, ) -> str:
        """
        Get nickname of style "@nickname" or "firstname lastname".
        "app.tg.ptb.config.Config.bot.get_chat" may block the execution if there are connection but no internet,
        the "timeout" parameter is ignoring, is this a bug of PTB/TG ?
        """
        if isinstance(entity, int):
            try:
                entity: telegram_Chat = app.tg.ptb.config.Config.bot.get_chat(chat_id=entity, timeout=timeout, )
            except (tg_errors_BadRequest, tg_errors_TimedOut):
                return ''
        if entity.username:
            return f'@{entity.username}'
        else:
            return entity.full_name

    def get_my_tg_name(self, timeout: int = 3) -> str:
        """
        Get nickname of style "@nickname" or "firstname lastname".
        "app.tg.ptb.config.Config.bot.get_chat" may block the execution if there are connection but no internet,
        the "timeout" parameter is ignoring, is this a bug of PTB/TG ?
        """
        return self.get_tg_name(entity=self.tg_user_id, timeout=timeout, )

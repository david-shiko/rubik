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
from typing import TYPE_CHECKING, Protocol
from abc import ABC, abstractmethod

from app.tg.classes.users import Profile, ProfileInterface
import app.constants
import app.models.base.users
import app.models.users

if TYPE_CHECKING:
    from psycopg2.extensions import connection as pg_ext_connection
    import app.structures.base
    import app.models.posts
    import app.models.collections


class UserInterface(app.models.users.UserInterface, ABC, ):
    @property
    @abstractmethod
    def is_tg_active(self) -> bool:  # Not in use mainly
        ...

    @is_tg_active.setter
    @abstractmethod
    def is_tg_active(self, value: bool):
        ...

    @property
    @abstractmethod
    def tg_name(self) -> str | None:
        ...

    @tg_name.setter
    @abstractmethod
    def tg_name(self, value: bool):
        ...

    @staticmethod
    @abstractmethod
    def get_tg_name(*rgs, **kwargs, ) -> str:
        """
        Get nickname of style "@nickname" or "firstname lastname".
        "app.tg.ptb.config.Config.bot.get_chat" may block the execution if there are connection but no internet,
        the "timeout" parameter is ignoring, is this a bug of PTB/TG ?
        """
        ...

    @classmethod
    @abstractmethod
    def from_user(cls, user: app.models.users.User) -> User:
        ...


class User(app.models.users.User, UserInterface, ):
    """User with methods of telegram"""

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
        # Check me
        self.profile: Profile = Profile(user=self, )
        self.tg_name = tg_name
        self._is_tg_active = is_tg_active

    @property
    def is_tg_active(self) -> bool:  # Not in use mainly
        raise NotImplementedError

    @is_tg_active.setter
    def is_tg_active(self, value: bool):
        raise NotImplementedError

    @property
    def tg_name(self) -> str | None:
        raise NotImplementedError

    @tg_name.setter
    def tg_name(self, value: bool):
        raise NotImplementedError

    def share_personal_posts(
            self,
            recipient: app.models.users.User,
            posts: list[app.models.posts.PersonalPost] | None = None,
    ) -> None:
        raise NotImplementedError

    def share_collections_posts(
            self,
            recipient: app.models.users.User,
    ) -> None:
        raise NotImplementedError

    @staticmethod
    def get_tg_name(*rgs, **kwargs, ) -> str:
        """
        Get nickname of style "@nickname" or "firstname lastname".
        "app.tg.ptb.config.Config.bot.get_chat" may block the execution if there are connection but no internet,
        the "timeout" parameter is ignoring, is this a bug of PTB/TG ?
        """
        raise NotImplementedError

    @classmethod
    def from_user(cls, user: app.models.users.User, ) -> User:
        """init with "vars" can't be used because of properties (_connection, etc.) are unexpected args"""
        ptb_user = cls(
            tg_user_id=user.tg_user_id,
            connection=user.connection,
            photos=user.photos,
            fullname=user.fullname,
            goal=user.goal,
            gender=user.gender,
            age=user.age,
            city=user.city,
            country=user.country,
            comment=user.comment,
            is_registered=user.is_registered,
        )
        ptb_user._matcher = user._matcher
        ptb_user.collections = user.collections
        if user._matcher is not None:
            ptb_user._matcher = ptb_user.Mapper.Matcher(user=user._matcher.user, filters=user._matcher.filters, )
        return ptb_user

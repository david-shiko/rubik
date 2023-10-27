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
from typing import TYPE_CHECKING, Protocol, Type, TypedDict
from dataclasses import dataclass

from app.structures.base import Goal, Gender
from app import constants
from app.models.users import User as UserModel, UserInterface as UserModelInterface
from app.models.mix import Photo as PhotoModel

if TYPE_CHECKING:
    pass


class ProfileText(TypedDict):
    name: str
    goal: str
    gender: str
    age: int
    location: str
    comment: str


class ProfileDataDB(ProfileText):
    photos: list[str]


class ProfileProtocol(Protocol, ):
    fullname: str
    goal: Goal
    gender: Gender
    age: int
    city: str
    country: str
    photos: list[str]
    comment: str
    is_loaded: bool


@dataclass(slots=True, )
class Payload:
    text: str
    photos: list[str]


class ProfileInterface(ProfileProtocol, ABC, ):
    Payload: Payload

    @abstractmethod
    def convert_text(self, ):
        ...

    @abstractmethod
    def get_data(self, ):
        ...

    @abstractmethod
    def get_db_data(self, ):
        ...

    @abstractmethod
    def load(self, ) -> None:
        ...

    @abstractmethod
    def convert_goal(self) -> str:
        ...

    @abstractmethod
    def convert_gender(self) -> str:
        ...

    @abstractmethod
    def get_profile_text(self) -> str:
        ...


class Profile(ProfileInterface, ):
    UserModel: Type[UserModel] = UserModel
    Payload: Type[Payload] = Payload

    SearchTranslationMap = {  # Rename to match?
        UserModel.Goal: {
            UserModel.Goal.CHAT: constants.Search.Profile.IT_WANNA_CHAT,
            UserModel.Goal.DATE: constants.Search.Profile.IT_WANNA_DATE,
            UserModel.Goal.BOTH: constants.Search.Profile.CHAT_AND_DATE,
        },
        UserModel.Gender: {
            UserModel.Gender.MALE: constants.Search.Profile.MALE,
            UserModel.Gender.FEMALE: constants.Search.Profile.FEMALE,
        },
    }

    RegTranslationMap = {
        UserModel.Goal: {
            UserModel.Goal.CHAT: constants.Reg.Profile.I_WANNA_CHAT,
            UserModel.Goal.DATE: constants.Reg.Profile.I_WANNA_DATE,
            UserModel.Goal.BOTH: constants.Reg.Profile.I_WANNA_CHAT_AND_DATE,
        },
        UserModel.Gender: {
            UserModel.Gender.MALE: constants.Reg.Profile.I_MALE,
            UserModel.Gender.FEMALE: constants.Reg.Profile.I_FEMALE,
        },
    }

    def __init__(
            self,
            user: UserModelInterface,
            profile: ProfileProtocol | None = None,
            load: bool = False,  # Is need to load profile data from db
    ):
        self.user = user
        self.profile = profile or user
        # TODO Quickfix. NewUser has no tg_user_id attr. Rewrite it to unique implementation
        self.tg_user_id = user.tg_user_id
        if isinstance(profile, self.UserModel, ):
            self.translations = self.SearchTranslationMap
        else:
            self.translations = self.RegTranslationMap
        self.is_loaded = not load  # If load not required that means it's already was loaded

    def convert_goal(self) -> str:
        """Attr may be None"""
        return self.translations[self.profile.Goal].get(self.profile.goal, constants.Shared.Words.UNKNOWN, )

    def convert_gender(self) -> str:
        """Attr may be None"""
        return self.translations[self.profile.Gender].get(self.profile.gender, constants.Shared.Words.UNKNOWN, )

    def convert_text(self, ) -> ProfileText:
        """Convert user attributes to human-readable views"""
        location = ', '.join(x for x in [self.profile.country, self.profile.city] if x is not None) or None
        text = {
            # Add link with user to a message. Don't forget to use parse_mode="HTML" if you are using links
            # TODO fullname or tg_name?
            constants.Shared.Profile.NAME: f"<a href='tg://user?id={self.tg_user_id}'>{self.profile.fullname}</a>",
            constants.Shared.Profile.GOAL: self.convert_goal(),
            constants.Shared.Profile.GENDER: self.convert_gender(),
            constants.Shared.Profile.AGE: self.profile.age,
            constants.Shared.Profile.LOCATION: location,
            constants.Shared.Profile.ABOUT: self.profile.comment,
        }
        return {k: v for k, v in text.items() if v is not None}

    def get_profile_text(self) -> str:
        text = '\n'.join([f'{k} - {v}.' for k, v in self.convert_text().items()])
        return text[:-1]  # Slice to remove trailing dot in the comment

    def get_data(self, ) -> Payload:
        """Get profile object"""
        if self.is_loaded is False:
            self.load()
        profile_text = self.get_profile_text()
        return self.Payload(text=profile_text, photos=self.user.photos, )

    def get_db_data(self) -> ProfileDataDB:
        """Get profile object from DB (?)"""
        profile_data = self.user.CRUD.read(tg_user_id=self.user.tg_user_id, connection=self.user.connection, ) or {}
        photos = PhotoModel.CRUD.read(tg_user_id=self.user.tg_user_id, connection=self.user.connection, )
        return ProfileDataDB(**profile_data, photos=photos, )

    def load(self) -> None:
        """Set profile data from DB"""
        for key, value in self.get_db_data().items():
            if value is not None:
                setattr(self.user, key, value)

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

from collections import UserDict
from enum import Enum, IntEnum
from typing import TypedDict, TYPE_CHECKING

from app.exceptions import DuplicateKeyError
import app.constants

if TYPE_CHECKING:
    pass


class UniqueKeyDict(UserDict):
    """
    Disable key overwriting if already exists
    Can be instantiated with any syntax style, i.e. (foo = foo, **{'foo': 'foo'}, {'foo': 'foo'})
    """

    def __setitem__(self, key=None, value=None, **kwargs, ):
        if key in self:
            raise DuplicateKeyError(f"Key '{key}' already exists with value '{self[key]}'")
        self.data[key] = value

    def force_update(self, *args, **kwargs, ) -> None:
        """See help({}.update)"""
        if len(args) > 0 and isinstance(args[0], dict):
            kwargs: dict = args[0]
        for key, value in kwargs.items():
            self.pop(key, None)  # First delete the key
            self[key] = value


class ReqRequiredActions(Enum):
    DEFAULT = app.constants.REG_REQUIRED
    SET_PUBLIC_VOTE = app.constants.Deprecated.REG_REQUIRED_FOR_VOTING
    SET_PERSONAL_VOTE = app.constants.Deprecated.REG_REQUIRED_FOR_VOTING


class Goal(IntEnum):  # Shared for user and matches
    CHAT = 1
    DATE = 2
    BOTH = 3


class Gender(IntEnum):  # Shared for user and matches
    MALE = 1
    FEMALE = 2


class Age(IntEnum):  # Shared for user and matches
    MIN = 10
    MAX = 99


class PublicPostDB(TypedDict):
    author: int
    post_id: int
    message_id: int
    likes_count: int
    dislikes_count: int
    status: int


class PersonalPostDB(TypedDict):
    post_id: int
    message_id: int
    author: int


class CollectionDB(TypedDict):
    collection_id: int
    author: int
    name: str


class PublicVoteDB(TypedDict):
    tg_user_id: int
    post_id: int
    message_id: int | None
    value: int | None


class UserPublicVote(TypedDict):
    post_id: int
    value: int


class UserPersonalVote(TypedDict):
    post_id: int
    value: int


class PersonalVoteDB(TypedDict):
    tg_user_id: int
    post_id: int
    message_id: int
    value: int | None


class UserDB(TypedDict, ):
    """DB record of user (without photos)"""
    tg_user_id: int
    fullname: str
    goal: int
    gender: int
    age: int
    country: str
    city: str
    comment: str


class PhotoDB(TypedDict):  # Not the same with raw user because here no photos
    tg_user_id: int
    tg_photo_file_id: str


class UserRaw(UserDB):
    """
    Raw static views for the user class.
    "static" because some attributes are assigned dynamically during instance initialization
    ("tg_name", "is_registered", etc)
    """
    photos: list[str]


class Covote(TypedDict):
    id: int
    tg_user_id: int
    count_common_interests: int


class ShownUserDB(TypedDict):
    tg_user_id: int
    shown_id: int


class PersonalVotesStatsDB(TypedDict):
    num_pos_votes: int
    num_neg_votes: int
    num_zero_votes: int

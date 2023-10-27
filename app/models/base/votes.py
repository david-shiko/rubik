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
from enum import IntEnum

from app.db import crud
from app.postconfig import logger
import app.structures.base

if TYPE_CHECKING:
    pass


class VoteBaseProtocol(Protocol, ):
    user: app.models.users.User
    post_id: int
    message_id: int | None
    value: Value


class VotableValue(IntEnum):
    POSITIVE = 1
    NEGATIVE = -1


class Value(IntEnum):
    POSITIVE = 1
    NEGATIVE = -1
    NONE = ZERO = 0


class VoteBaseInterface(VoteBaseProtocol, ABC):
    """
     Commot methods for both classes, PublicVote and PersonalVote.
     User may vote only if vote present in DB -  that's condition of app (insertion during sending)
     """

    VotableValue: VotableValue
    Value: Value

    @abstractmethod
    def __repr__(self, ) -> str:
        ...

    @abstractmethod
    def is_accept_vote(self, new_vote: VoteBaseInterface, ) -> bool:
        """Raise?  Accept only after "post.accept" because value will be changed."""
        ...

    @classmethod
    @abstractmethod
    def convert_vote_value(
            cls,
            raw_value: int | None,
            only_votable: bool = True,
    ) -> Value | VotableValue:
        """
        Convert any number to vote value
        None become a zero
        """
        ...


class VoteBase(VoteBaseInterface, ):
    """
     Commot methods for both classes, PublicVote and PersonalVote.
     User may vote only if vote present in DB -  that's condition of app (insertion during sending)
     """
    Value = Value
    VotableValue = VotableValue

    def __init__(
            self,
            user: app.models.users.User,
            post_id: int,
            message_id: int | None,
            value: Value = Value.NONE,
    ):
        self.user: app.models.users.User = user
        self.value: Value = value
        self.post_id: int = post_id
        self.message_id: int | None = message_id

    def __repr__(self, ):
        d = {
            'self': object.__repr__(self),
            'user': self.user,
            'post_id': self.post_id,
            'message_id': self.message_id,
            'value': self.value,
        }
        return repr({k: v for k, v in d.items() if v is not None}) + '\n'

    def is_accept_vote(self, new_vote: VoteBaseInterface, ) -> bool:
        """Raise?  Accept only after "post.accept" because value will be changed."""
        return self.value.value + new_vote.value.value in list(self.Value)

    @classmethod
    def convert_vote_value(cls, raw_value: int | None, only_votable: bool = True, ) -> Value | VotableValue:
        """
        Convert any number to vote value
        None become a zero
        """
        raw_value = raw_value or 0  # Convert None to zero
        if only_votable is True and raw_value == 0:
            logger.warning(
                msg='"only_votable=True" was used on 0 value. 0 can not be VotableValue. Silently set to False.',
            )
            only_votable = False
        if only_votable:
            value_cls = cls.VotableValue
        else:
            value_cls = cls.Value
        if raw_value > (max_value := max(value_cls)):
            return max_value
        elif raw_value < (min_value := min(value_cls)):
            return min_value
        else:
            return value_cls(raw_value)


class PublicVoteInterface(VoteBaseInterface, ABC, ):
    @abstractmethod
    def update(self, ) -> None:
        ...

    @abstractmethod
    def upsert_value(self, ) -> None:
        ...

    @classmethod
    @abstractmethod
    def read_user_votes_count(cls, user: app.models.users.User, ) -> int:
        ...


class PublicVote(VoteBase, PublicVoteInterface, ):
    CRUD = crud.votes.PublicVote

    def update(self, ) -> None:
        return self.CRUD.update(
            tg_user_id=self.user.tg_user_id,
            post_id=self.post_id,
            value=self.value.value,  # int, real value of vote value
            connection=self.user.connection,
        )

    def upsert_value(self, ) -> None:
        return self.CRUD.upsert_value(
            tg_user_id=self.user.tg_user_id,
            post_id=self.post_id,
            message_id=self.message_id,
            value=self.value.value,  # int, real value of vote value
            connection=self.user.connection,
        )

    @classmethod
    def read_user_votes_count(cls, user: app.models.users.User, ) -> int:
        return cls.CRUD.read_user_votes_count(tg_user_id=user.tg_user_id, connection=user.connection, )


class PersonalVoteInterface(VoteBaseInterface, ABC, ):
    @abstractmethod
    def upsert(self, message_id: int, ) -> None:
        ...


class PersonalVote(VoteBase, PersonalVoteInterface, ):
    """If vote is empty value - ZERO"""
    CRUD = crud.votes.PersonalVote

    def upsert(self, message_id: int, ) -> None:
        return self.CRUD.upsert(
            tg_user_id=self.user.tg_user_id,
            post_id=self.post_id,
            message_id=message_id or self.message_id,
            value=self.value.value,  # int, real value of vote value
            connection=self.user.connection,
        )

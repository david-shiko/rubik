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
from typing import Type, TYPE_CHECKING, TypeVar
from dataclasses import dataclass

from app.models import base
from app.db import crud

if TYPE_CHECKING:
    from app.models import PublicVoteMapper, PersonalVoteMapper
    from app.models.users import UserInterface
    from app.models.posts import PublicPostInterface, PersonalPostInterface


class PublicVoteInterface(base.votes.PublicVoteInterface, ABC):

    Mapper: PublicVoteMapper
    CRUD: crud.votes.PublicVote
    Shared: Type[Shared]

    @classmethod
    @abstractmethod
    def read_vote(cls, user: UserInterface, post_id: int, ) -> PublicVote:
        ...

    @classmethod
    @abstractmethod
    def read(
            cls,
            post_id: int,
            user: UserInterface,
    ) -> PublicVoteInterface | None:
        ...

    @classmethod
    @abstractmethod
    def get_user_vote(
            cls,
            user: UserInterface,
            post: PublicPostInterface
    ) -> PublicVoteInterface:
        ...

    @classmethod
    @abstractmethod
    def get_user_votes(cls, user: UserInterface, ) -> list[PublicVote]:
        ...


class PersonalVoteInterface(base.votes.PersonalVoteInterface, ABC, ):

    Mapper: PersonalVoteMapper
    CRUD: crud.votes.PersonalVote
    Shared: Type[Shared]

    @classmethod
    @abstractmethod
    def read(
            cls,
            user: UserInterface,
            post_id: int,
    ) -> PersonalVoteInterface | None:
        ...

    @classmethod
    @abstractmethod
    def read_vote(
            cls,
            user: UserInterface,
            post_id: int
    ) -> PersonalVote:
        ...

    @classmethod
    @abstractmethod
    def get_user_votes(cls, user: UserInterface) -> list[PersonalVote]:
        ...

    @abstractmethod
    def handle(self, ) -> PersonalVote.HandledVote:
        ...

    @classmethod
    @abstractmethod
    def get_user_vote(
            cls,
            user: UserInterface,
            post: PersonalPostInterface
    ) -> PersonalVoteInterface:
        ...


T1 = TypeVar('T1', bound=PublicVoteInterface)
T2 = TypeVar('T2', bound=PersonalVoteInterface)


class Shared:
    @staticmethod
    def get_user_vote(
            cls: Type[T1 | T2],
            user: UserInterface,
            post: PublicPostInterface | PersonalPostInterface
    ) -> T1 | T2:
        """Common method for both classes"""
        vote = cls.read(user=user, post_id=post.post_id, )
        if not vote:
            vote = cls(user=user, post_id=post.post_id, message_id=None, )
        return vote


class PublicVote(base.votes.PublicVote, PublicVoteInterface, ):
    """If vote is empty value - ZERO"""

    Mapper: PublicVoteMapper
    CRUD = crud.votes.PublicVote
    Shared = Shared

    @dataclass
    class HandledVote:
        new_value: base.votes.VoteBase.Value
        old_value: base.votes.VoteBase.Value
        incoming_value: base.votes.VoteBase.Value
        is_accepted: bool

    @classmethod
    def read_vote(cls, user: UserInterface, post_id: int, ) -> PublicVote:
        """Guaranty to return vote instance"""
        vote = (
                cls.read(user=user, post_id=post_id) or
                cls(user=user, post_id=post_id, message_id=None, value=cls.Value.NONE, )
        )
        return vote

    @classmethod
    def read(
            cls,
            post_id: int,
            user: UserInterface,
    ) -> PublicVote | None:
        vote_row = cls.CRUD.read(post_id=post_id, tg_user_id=user.tg_user_id, connection=user.connection, )
        if vote_row:
            return cls(
                user=user,
                post_id=vote_row['post_id'],
                message_id=vote_row['message_id'],
                value=cls.Value(vote_row['value']),
            )
        return None

    @classmethod
    def get_user_votes(cls, user: UserInterface, ) -> list[PublicVote]:
        """
        Returns all (included non-votable (Zero or None)) votes from common table. Not in use currently.
        To read only votable cached votes - use Matcher.get_user_votes (preferred).
        """
        vote_rows = cls.CRUD.read_user_votes(tg_user_id=user.tg_user_id, connection=user.connection, )
        result = []
        for vote_row in vote_rows:
            result.append(
                cls(
                    user=user,
                    post_id=vote_row['post_id'],
                    message_id=vote_row['message_id'],
                    value=cls.Value(vote_row['value']),
                )
            )
        return result

    def handle(self, ) -> HandledVote:
        """Handle self (incoming vote)"""
        is_accepted = False
        incoming_value: base.votes.VoteBase.Value = self.value  # Before change
        old_vote = self.read_vote(user=self.user, post_id=self.post_id, )  # Only for checking
        if old_vote.is_accept_vote(new_vote=self, ) is True:
            self.value: base.votes.VoteBase.Value = self.Value(self.value + old_vote.value)
            self.upsert_value()
            is_accepted = True
        return self.HandledVote(
            new_value=self.value,
            old_value=old_vote.value,
            incoming_value=incoming_value,
            is_accepted=is_accepted
        )

    @classmethod
    def get_user_vote(
            cls,
            user: UserInterface,
            post: PublicPostInterface
    ) -> PublicVote:
        return cls.Shared.get_user_vote(cls=cls, post=post, user=user, )


class PersonalVote(base.votes.PersonalVote, PersonalVoteInterface, ):
    """If vote is empty value - ZERO"""
    Mapper: PersonalVoteMapper
    CRUD = crud.votes.PersonalVote
    Shared = Shared

    @dataclass
    class HandledVote:
        new_vote: PersonalVote
        old_vote: PersonalVote
        is_accepted: bool

    @classmethod
    def read(
            cls,
            user: UserInterface,
            post_id: int,
    ) -> PersonalVote | None:
        vote_row = cls.CRUD.read(tg_user_id=user.tg_user_id, post_id=post_id, connection=user.connection, )
        if vote_row is not None:
            vote_row['value'] = cls.Value(vote_row['value'])
            # noinspection PyTypedDict
            del vote_row['tg_user_id']
            return cls(user=user, **vote_row)
        return None

    @classmethod
    def read_vote(
            cls,
            user: UserInterface,
            post_id: int
    ) -> PersonalVote:
        """Guaranty to return vote instance"""
        return (
                cls.read(user=user, post_id=post_id, ) or
                cls(user=user, post_id=post_id, message_id=None, value=cls.Value.ZERO)  # ZERO ?
        )

    @classmethod
    def get_user_votes(cls, user: UserInterface) -> list[PersonalVote]:
        """Returns all (included non-votable (Zero or None)) votes from common table. Not in use currently."""
        vote_rows = cls.CRUD.read_user_votes(tg_user_id=user.tg_user_id, connection=user.connection, )
        result = []
        for vote_row in vote_rows:
            result.append(
                cls(
                    user=user,
                    post_id=vote_row['post_id'],
                    message_id=vote_row['message_id'],
                    value=cls.convert_vote_value(raw_value=vote_row['value'], only_votable=False),
                )
            )
        return result

    def handle(self, ) -> PersonalVote.HandledVote:
        old_vote = self.read_vote(user=self.user, post_id=self.post_id, )  # Only for checking
        if old_vote.is_accept_vote(new_vote=self, ) is True:
            self.upsert(message_id=self.message_id, )
            return self.HandledVote(new_vote=self, old_vote=old_vote, is_accepted=True, )
        return self.HandledVote(new_vote=self, old_vote=old_vote, is_accepted=False, )

    @classmethod
    def get_user_vote(
            cls,
            user: UserInterface,
            post: PersonalPostInterface
    ) -> PersonalVote:
        return cls.Shared.get_user_vote(cls=cls, post=post, user=user, )

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

from psycopg2.extensions import connection as pg_ext_connection

from app.models import base

if TYPE_CHECKING:
    from app.models import UserMapper
    from app.models.matches import MatchInterface, MatcherInterface
    from app.models.votes import PublicVoteInterface, PersonalVoteInterface
    from app.models.posts import PublicPostInterface, PersonalPostInterface
    from app.models.collections import CollectionInterface

Goal = base.users.User.Goal
Age = base.users.User.Age


class UserInterface(base.users.UserInterface, ABC, ):

    collections: list[CollectionInterface]
    matcher: MatcherInterface | None

    @property
    @abstractmethod
    def matcher(self) -> MatchInterface:
        ...

    @matcher.setter
    @abstractmethod
    def matcher(self, value: MatchInterface, ):
        ...

    @abstractmethod
    def __repr__(self) -> str:
        ...

    @abstractmethod
    def get_new_public_post(self, ) -> PublicPostInterface | None:
        ...

    @abstractmethod
    def get_personal_posts(self, ) -> list[PersonalPostInterface]:
        ...

    @abstractmethod
    def get_vote(
            self,
            post: PublicPostInterface | PersonalPostInterface,
    ) -> PublicVoteInterface | PersonalVoteInterface:
        ...

    @abstractmethod
    def set_vote(
            self,
            vote: PublicVoteInterface | PersonalVoteInterface,
            post: PublicPostInterface | PersonalPostInterface = None,
    ) -> bool:
        ...

    @abstractmethod
    def get_personal_votes(self, ) -> list[PersonalVoteInterface]:
        ...

    @abstractmethod
    def create_collection(
            self,
            posts: list[PersonalPostInterface],
            name: str,
    ) -> None:
        ...

    @abstractmethod
    def get_collections(
            self,
            ids: list[int] = None,
            cache: bool = True,
    ) -> list[CollectionInterface]:
        ...

    @abstractmethod
    def delete_photos(self, ) -> None:
        ...

    @abstractmethod
    def upsert_shown_post(self, new_message_id: int, public_post: PublicPostInterface, ) -> None:
        ...

    @abstractmethod
    def share_collections_posts(
            self: UserInterface,
            recipient: UserInterface,
    ) -> None:
        ...

    @abstractmethod
    def share_personal_posts(
            self,
            recipient: UserInterface,
            posts: list[PersonalPostInterface] | None = None,
    ) -> None:
        ...


class User(base.users.User, UserInterface, ):
    """Base User Logic across whole app (only logic actions)"""

    Mapper: UserMapper

    def __init__(
            self,
            tg_user_id: int,
            connection: pg_ext_connection | None = None,
            fullname: str | None = None,
            goal: Goal | None = None,
            gender: User.Gender | None = None,
            age: int | None = None,
            country: str | None = None,
            city: str | None = None,
            comment: str | None = None,
            photos: list[str] | None = None,
            is_registered: bool | None = None,
    ):
        super().__init__(
            tg_user_id=tg_user_id,
            connection=connection,
            fullname=fullname,
            goal=goal,
            gender=gender,
            age=age,
            city=city,
            country=country,
            comment=comment,
            photos=photos,
            is_registered=is_registered,
        )
        self.collections: list[CollectionInterface] = []  # Move me to cache object
        self.matcher: MatcherInterface | None = None

    def __repr__(self) -> str:
        return repr(self._repr() | {'tg_user_id': self.tg_user_id})

    @property
    def matcher(self, ) -> MatcherInterface:
        self._matcher = self._matcher or self.Mapper.Matcher(user=self, )
        return self._matcher

    @matcher.setter
    def matcher(self, value: MatcherInterface, ):
        self._matcher = value

    def get_new_public_post(self, ) -> PublicPostInterface | None:
        return self.Mapper.PublicPost.read_exclusive(user=self, )

    def get_personal_posts(self, ) -> list[PersonalPostInterface]:
        return self.Mapper.PersonalPost.read_user_posts(user=self, )

    def get_vote(
            self,
            post: PublicPostInterface | PersonalPostInterface,
    ) -> PublicVoteInterface | PersonalVoteInterface:
        return post.Mapper.Vote.get_user_vote(user=self, post=post, )

    def set_vote(
            self,
            vote: PublicVoteInterface | PersonalVoteInterface,
            post: PublicPostInterface | PersonalPostInterface = None,
    ) -> bool:
        handled_vote = vote.handle()  # Validate + save (any vote type)
        if handled_vote.is_accepted is True:
            post = post or vote.Mapper.Post.get_post_by_vote(vote=vote, )
            if isinstance(post, self.Mapper.PublicPost) and isinstance(vote, self.Mapper.PublicVote):
                self.matcher.is_user_has_votes = True
            return post.handle_vote(handled_vote=handled_vote, )  # Only public post need to be handled
        return False

    def get_personal_votes(self, ) -> list[PersonalVoteInterface]:
        return self.Mapper.PersonalVote.get_user_votes(user=self, )

    def create_collection(
            self,
            posts: list[PersonalPostInterface],
            name: str = None,  # On definition stage DEFAULT_NAME yet not exists cuz taken from self
    ) -> None:
        self.Mapper.Collection.create(
            author=self,
            name=name or self.Mapper.Collection.DEFAULT_NAME,
            posts_ids=[post.post_id for post in posts],
        )

    def get_collections(
            self,
            ids: list[int] = None,
            cache: bool = True,
    ) -> list[CollectionInterface]:
        if ids is not None:
            result = self.Mapper.Collection.get_by_ids(user=self, ids=ids, )
        else:
            result = self.Mapper.Collection.get_user_collections(author=self, )
        if cache is True:
            self.collections.extend(result)
        return result

    def delete_photos(self, ) -> None:
        return self.Mapper.Photo.delete_user_photos(user=self)

    def upsert_shown_post(self, new_message_id: int, public_post: PublicPostInterface, ) -> None:
        """Save new message_id of shown post to DB (Not sure that it should be here)"""
        self.Mapper.PublicVote.CRUD.upsert_message_id(
            tg_user_id=self.tg_user_id,
            post_id=public_post.post_id,
            new_message_id=new_message_id,
            connection=self.connection,
        )

    def share_collections_posts(
            self: UserInterface,
            recipient: UserInterface,
    ) -> None:
        raise NotImplemented

    def share_personal_posts(
            self,
            recipient: UserInterface,
            posts: list[PersonalPostInterface] | None = None,
    ) -> None:
        raise NotImplemented

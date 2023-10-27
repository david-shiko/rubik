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
from dataclasses import dataclass

from app.models import base

if TYPE_CHECKING:
    from psycopg2.extensions import connection as pg_ext_connection
    import app.structures.base
    from app.models import PublicPostMapper, PersonalPostMapper
    from app.models.votes import PublicVoteInterface, PersonalVoteInterface
    from app.models.users import UserInterface


class PostBase(ABC, ):

    @classmethod
    def read(cls, *args, **kwargs, ):
        raise NotImplemented

    @classmethod
    def get_post_by_vote(
            cls,
            vote: PublicVoteInterface | PersonalVoteInterface,
    ) -> PublicPostInterface | PersonalPostInterface:
        return cls.read(post_id=vote.post_id, connection=vote.user.connection, )


class PublicPostInterface(base.posts.PublicPostInterface, ABC):
    Mapper: PublicPostMapper

    @classmethod
    @abstractmethod
    def read(cls, post_id: int, connection: pg_ext_connection, ) -> PublicPostInterface | None:
        ...

    @classmethod
    @abstractmethod
    def get_post_by_vote(cls, vote: PublicVoteInterface, ) -> PublicPostInterface:
        ...

    @classmethod
    @abstractmethod
    def read_exclusive(
            cls,
            user: UserInterface,
            status: base.posts.PublicPostInterface.Status = None,
    ) -> PublicPostInterface | None:
        ...

    @classmethod
    @abstractmethod
    def read_mass(
            cls,
            status: base.posts.PublicPostInterface.Status = None,
    ) -> PublicPostInterface | None:
        ...

    @classmethod
    @abstractmethod
    def db_to_cls(
            cls, post_row: app.structures.base.PublicPostDB, connection: pg_ext_connection, ) -> PublicPostInterface:
        ...

    @classmethod
    @abstractmethod
    def dbs_to_cls(
            cls,
            posts_rows: list[app.structures.base.PublicPostDB],
            connection: pg_ext_connection,
    ) -> list[PublicPost]:
        ...

    @abstractmethod
    def accept_vote_value(
            self,
            incoming_value: PublicVoteInterface.VotableValue,
            old_value: PublicVoteInterface.VotableValue,
    ) -> bool:
        ...

    @abstractmethod
    def handle_vote(self, handled_vote: PublicVoteInterface.HandledVote, ) -> bool:
        ...

    @abstractmethod
    def get_voted_users(self, connection: pg_ext_connection, ) -> list[UserInterface]:
        ...


class PublicPost(base.posts.PublicPost, PostBase, PublicPostInterface, ):
    Mapper: PublicPostMapper

    @classmethod
    def db_to_cls(
            cls, post_row: app.structures.base.PublicPostDB, connection: pg_ext_connection, ) -> PublicPostInterface:
        """Convert post from db to post object"""
        return cls(
            author=cls.Mapper.User(tg_user_id=post_row['author'], connection=connection, ),
            post_id=post_row['post_id'],
            message_id=post_row['message_id'],
            likes_count=post_row['likes_count'],
            dislikes_count=post_row['dislikes_count'],
            status=cls.Status(post_row['status']),
        )

    @classmethod
    def dbs_to_cls(
            cls,
            posts_rows: list[app.structures.base.PublicPostDB],
            connection: pg_ext_connection,
    ) -> list[PublicPostInterface]:
        """Convert post from db to post object"""
        result = []
        for post_row in posts_rows:
            result.append(cls.db_to_cls(post_row=post_row, connection=connection, ))
        return result

    @classmethod
    def read(cls, post_id: int, connection: pg_ext_connection, ) -> PublicPostInterface | None:
        post_row = cls.CRUD.read(post_id=post_id, connection=connection, )
        if post_row is not None:
            return cls.db_to_cls(post_row=post_row, connection=connection)
        return None

    @classmethod
    def read_exclusive(
            cls,
            user: UserInterface,
            status: base.posts.PublicPostInterface.Status = None,
    ) -> PublicPostInterface | None:
        """Read post to send to personal user"""
        status = status if status is not None else cls.Status.READY_TO_RELEASE  # Not or because status may be 0
        post_row = cls.CRUD.read_exclusive(
            tg_user_id=user.tg_user_id,
            status=status.value,
            connection=user.connection,
        )
        if post_row is not None:
            return cls.db_to_cls(post_row=post_row, connection=user.connection, )
        return None

    @classmethod
    def read_mass(
            cls,
            status: base.posts.PublicPostInterface.Status = None,
    ) -> PublicPostInterface | None:
        """
        Read post to send to group of users
        """
        if status is None:
            status = cls.Status.READY_TO_RELEASE
        post_row = cls.CRUD.read_mass(connection=cls.CRUD.db.connection, status=status.value, )
        if post_row is not None:
            return cls.db_to_cls(post_row=post_row, connection=cls.CRUD.db.connection, )
        return None

    def accept_vote_value(
            self,
            incoming_value: PublicVoteInterface.VotableValue,
            old_value: PublicVoteInterface.VotableValue,
    ) -> bool:
        """
        Raise?  Accept only BEFORE vote.accept because value will be changed.
        Separate check logic for post (theoretically may differ from a vote logic.
        Not use set, order are matter.
        """
        positive = self.Mapper.Vote.Value.POSITIVE
        zero = self.Mapper.Vote.Value.ZERO
        negative = self.Mapper.Vote.Value.NEGATIVE
        if (old_value, incoming_value) == (zero, positive):
            self.likes_count += 1  # Replace on self constant
        elif (old_value, incoming_value) == (zero, negative):
            self.dislikes_count += 1
        elif (old_value, incoming_value) == (positive, negative):
            self.likes_count -= 1
        elif (old_value, incoming_value) == (negative, positive):
            self.dislikes_count -= 1
        else:
            return False
        return True

    def handle_vote(self, handled_vote: PublicVoteInterface.HandledVote, ) -> bool:
        is_vote_value_accepted = self.accept_vote_value(
            old_value=handled_vote.old_value,
            incoming_value=handled_vote.incoming_value,
        )
        if is_vote_value_accepted and handled_vote.is_accepted:
            self.update_votes_count()
            return True
        return False

    def get_voted_users(self, connection: pg_ext_connection, ) -> list[UserInterface]:
        voted_users = []
        users_ids = self.CRUD.read_voted_users_ids(post_id=self.post_id, connection=connection, )
        for user_id in users_ids:
            voted_users.append(self.Mapper.User(tg_user_id=user_id, connection=connection, ))
        return voted_users


class PersonalPostInterface(base.posts.PersonalPostInterface, ABC, ):

    @classmethod
    @abstractmethod
    def get_post_by_vote(cls, vote: PersonalVoteInterface, ) -> PersonalPostInterface:
        ...

    @classmethod
    @abstractmethod
    def read(cls, post_id: int, connection: pg_ext_connection, ) -> PersonalPost | None:
        ...

    @staticmethod
    @abstractmethod
    def handle_vote(handled_vote: PersonalVoteInterface.HandledVote, ) -> bool:
        ...


class PersonalPost(base.posts.PersonalPost, PostBase, PersonalPostInterface, ):
    Mapper: PersonalPostMapper

    @classmethod
    def db_to_cls(
            cls,
            post_row: app.structures.base.PersonalPostDB,
            connection: pg_ext_connection,
            author: UserInterface = None,
    ) -> PersonalPost:
        """Convert post from db to post object"""
        return cls(
            author=author or cls.Mapper.User(tg_user_id=post_row['author'], connection=connection, ),
            post_id=post_row['post_id'],
            message_id=post_row['message_id'],
        )

    @classmethod
    def dbs_to_cls(
            cls,
            posts_rows: list[app.structures.base.PersonalPostDB],
            connection: pg_ext_connection,
    ) -> list[PersonalPost]:
        """Convert list of posts from db to list if posts objects"""
        result = []
        for post_row in posts_rows:
            result.append(cls.db_to_cls(post_row=post_row, connection=connection, ))
        return result

    @classmethod
    def read(
            cls,
            post_id: int,
            connection: pg_ext_connection,
            author: UserInterface = None,
    ) -> PersonalPost | None:
        post_row = cls.CRUD.read(post_id=post_id, connection=connection, )
        if post_row:  # If not found behavior?
            return cls.db_to_cls(post_row=post_row, connection=connection, author=author, )
        return None

    @staticmethod
    def handle_vote(handled_vote: PersonalVoteInterface.HandledVote, ) -> bool:
        return True  # no checking or saving for now


class VotedPublicPostInterface:
    """Public post that has a vote"""
    post: PublicPostInterface
    clicker_vote: PersonalVoteInterface

    @classmethod
    @abstractmethod
    def convert(
            cls,
            posts: list[PublicPost],
            clicker: UserInterface,
    ) -> list[VotedPublicPost]:
        ...


@dataclass(slots=True, )
class VotedPublicPost(VotedPublicPostInterface, ):
    """Public post that has a vote"""
    post: PublicPostInterface
    clicker_vote: PublicVoteInterface

    @classmethod
    def convert(
            cls,
            posts: list[PublicPost],
            clicker: UserInterface,
    ) -> list[VotedPublicPost]:
        voted_posts = []  # Move to method ?
        for post in posts:
            # Mypy unable to bind Post.Mapper.Vote to Vote
            voted_posts.append(cls(post=post, clicker_vote=clicker.get_vote(post=post), ))  # type: ignore[arg-type]
        return voted_posts


class VotedPersonalPostInterface:
    """Personal post that has a vote"""
    post: PersonalPostInterface
    clicker_vote: PersonalVoteInterface
    opposite_vote: PersonalVoteInterface

    @classmethod
    @abstractmethod
    def convert(
            cls,
            posts: list[PersonalPost],
            clicker: UserInterface,
            opposite: UserInterface,
    ) -> list[VotedPersonalPost]:
        ...


@dataclass(slots=True, )
class VotedPersonalPost(VotedPersonalPostInterface, ):
    """Personal post that has a vote"""
    post: PersonalPostInterface
    clicker_vote: PersonalVoteInterface
    opposite_vote: PersonalVoteInterface

    @classmethod
    def convert(
            cls,
            posts: list[PersonalPost],
            clicker: UserInterface,
            opposite: UserInterface,
    ) -> list[VotedPersonalPost]:
        voted_posts = []
        for post in posts:
            voted_posts.append(
                cls(
                    post=post,
                    # Mypy unable to bind Post.Mapper.Vote to Vote
                    clicker_vote=clicker.get_vote(post=post, ),  # type: ignore[arg-type]
                    # Mypy unable to bind Post.Mapper.Vote to Vote
                    opposite_vote=opposite.get_vote(post=post, ),  # type: ignore[arg-type]
                )
            )
        return voted_posts

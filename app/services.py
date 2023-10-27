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
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Type, TypeAlias

from app.generation import generator
from app.db import manager as db_manager

from app.models.posts import PublicPost as PublicPostModel
from app.forms.post import PublicPost as PublicPostForm

import app.db.crud.mix
import app.models.users
import app.models.collections

if TYPE_CHECKING:
    from psycopg2.extensions import connection as pg_ext_connection
    from app.models.posts import (
        PublicPostInterface as PublicPostModelInterface,
        PersonalPostInterface as PersonalPostModelInterface,
    )
    from app.forms.post import (
        PublicPostInterface as PublicPostFormInterface,
        PersonalPostInterface as PersonalPostFormInterface,
    )

    from app.forms.user import NewUserInterface as NewUserFormInterface


class PublicPostInterface(ABC, ):

    @classmethod
    @abstractmethod
    def get_pending_posts(
            cls,
            connection: pg_ext_connection,
    ) -> list[PublicPostModel]:
        ...


class PublicPost(PublicPostInterface):

    class Mapper:
        PublicPost = PublicPostModel
        DB = db_manager.Postgres

    @classmethod
    def get_pending_posts(
            cls,
            connection: pg_ext_connection,
    ) -> list[PublicPostModel]:
        """RETURNS posts with status 0 ("PENDING") from DB"""
        raw_posts = cls.Mapper.PublicPost.CRUD.read_public_posts_by_status(
            status=cls.Mapper.PublicPost.Status.PENDING,
            connection=connection,
        )
        posts = cls.Mapper.PublicPost.dbs_to_cls(posts_rows=raw_posts, connection=connection, )
        return posts

    @classmethod
    def get_public_posts(
            cls,
            connection: pg_ext_connection,
    ) -> list[PublicPostModelInterface]:
        """RETURNS posts with status 0 ("PENDING") from DB"""
        posts_ids = cls.Mapper.DB.read(
            statement=cls.Mapper.DB.sqls.PublicPosts.READ_PUBLIC_POSTS_IDS,
            fetch='fetchall',
            connection=connection,
        )
        posts = []
        for post_id in posts_ids:
            post = cls.Mapper.PublicPost.read(post_id=post_id, connection=connection, )
            if post is not None:
                posts.append(post)
        return posts


class SystemInterface(ABC):
    class Mapper(ABC):
        user: app.models.users.User

    CRUD: app.db.crud.mix.System
    connection: pg_ext_connection
    user: app.models.users.User

    @classmethod
    @abstractmethod
    def set_bots_votes_to_post(
            cls,
            post: PublicPostModelInterface | PersonalPostModelInterface,
            bots_ids: list[int] = None,
    ) -> None:
        ...

    @classmethod
    @abstractmethod
    def gen_bot(cls, bot_id: int, ) -> None:
        ...

    @classmethod
    @abstractmethod
    def gen_bots(cls, bots_ids: list[int]) -> None:
        ...

    @classmethod
    @abstractmethod
    def read_bots_ids(cls, ) -> list[int]:
        ...

    @classmethod
    @abstractmethod
    def read_all_users_ids(cls, ) -> list[int]:
        ...


class System(SystemInterface, ):
    class Mapper:
        User = app.models.users.User
        PublicPost = PublicPostModel

    CRUD: Type[app.db.crud.mix.System] = app.db.crud.mix.System
    user = Mapper.User(tg_user_id=app.config.BOT_ID, is_registered=True, )
    connection = user.connection
    generator = generator
    PublicPostService = PublicPost

    @classmethod
    def set_bots_votes_to_post(
            cls,
            post: PublicPostModelInterface | PersonalPostModelInterface,
            bots_ids: list[int] | None = None,
    ) -> None:
        for user_id in bots_ids or cls.CRUD.read_bots_ids(connection=cls.connection, ):
            bot = cls.Mapper.User(tg_user_id=user_id, connection=cls.connection, )
            vote = cls.generator.gen_vote(user=bot, post=post, )
            bot.set_vote(vote=vote, post=post, )

    @classmethod
    def set_bots_votes_to_posts(
            cls,
            posts: list[PublicPostModelInterface | PersonalPostModelInterface],
            bots_ids: list[int] = None,
    ) -> None:
        bots_ids = bots_ids or cls.CRUD.read_bots_ids(connection=cls.connection, )
        for post in posts:
            cls.set_bots_votes_to_post(post=post, bots_ids=bots_ids, )

    @classmethod
    def gen_bot(cls, bot_id: int, ) -> None:
        new_user: NewUserFormInterface = cls.generator.gen_new_user(tg_user_id=bot_id, )
        new_user.create()

    @classmethod
    def gen_bots(cls, bots_ids: list[int], gen_votes: bool = True, ) -> None:
        if gen_votes:
            posts = cls.PublicPostService.get_public_posts(connection=cls.connection, )
            for post in posts:
                cls.set_bots_votes_to_post(post=post, bots_ids=bots_ids, )
        for bot_id in bots_ids:
            cls.gen_bot(bot_id=bot_id, )

    @classmethod
    def read_bots_ids(cls, ) -> list[int]:
        bots_ids = cls.CRUD.read_bots_ids(connection=cls.connection, )
        return bots_ids

    @classmethod
    def read_all_users_ids(cls, ) -> list[int]:
        all_users_ids = cls.CRUD.read_all_users_ids(connection=cls.connection, )
        return all_users_ids


class CollectionInterface(ABC, ):
    class NamePrefix(ABC):
        PUBLIC: str
        PERSONAL: str

    CONNECTION: pg_ext_connection
    user: app.models.users.User

    class Mapper(ABC):
        Model: app.models.collections.Collection

    @classmethod
    @abstractmethod
    def get_defaults_names(cls, prefix: Collection.NamePrefix, ) -> list[str]:
        ...

    @classmethod
    @abstractmethod
    def get_defaults(cls, prefix: str, ) -> list[app.models.collections.CollectionInterface]:
        ...

    @classmethod
    @abstractmethod
    def create_default(
            cls,
            posts: list[PublicPostModelInterface | PersonalPostModelInterface],
            prefix: Collection.NamePrefix,
            name: str
    ):
        ...

    @classmethod
    @abstractmethod
    def get_by_ids(
            cls,
            ids: list[int],
            user: app.models.users.UserInterface,
    ) -> list[app.models.collections.CollectionInterface]:
        ...

    @classmethod
    @abstractmethod
    def remove_prefixes(cls, collections: list[app.models.collections.CollectionInterface], ):
        ...


class Collection(CollectionInterface, ):
    class NamePrefix(Enum):
        PUBLIC = 'public'
        PERSONAL = 'personal'

    class Mapper(ABC):
        Model: Type[app.models.collections.Collection] = app.models.collections.Collection
        # noinspection PyTypeHints
        ModelInterface: TypeAlias = app.models.collections.CollectionInterface

    user = System.user
    connection = System.user.connection

    @classmethod
    def remove_prefixes(cls, collections: list[Mapper.ModelInterface], ) -> None:
        for collection in collections:
            collection.name = cls.remove_prefix(name=collection.name, )

    @classmethod
    def remove_prefix(cls, name: str, ) -> str:
        name = name.replace(f'{cls.NamePrefix.PUBLIC.value}_', '')
        name = name.replace(f'{cls.NamePrefix.PERSONAL.value}_', '')
        return name

    @classmethod
    def get_defaults_names(cls, prefix: Collection.NamePrefix, ) -> list[str]:
        collections = cls.Mapper.Model.get_defaults_names(
            prefix=prefix.value,
            connection=cls.user.connection,
        )
        return [cls.remove_prefix(name=name, ) for name in collections]

    @classmethod
    def get_defaults(cls, prefix: str, ) -> list[app.models.collections.Collection]:
        collections = cls.Mapper.Model.get_defaults(
            prefix=prefix,
            author=cls.user,
        )
        cls.remove_prefixes(collections=collections, )
        return collections

    @classmethod
    def create_default(
            cls,
            posts: list[PublicPostModelInterface | PersonalPostModelInterface],
            prefix: Collection.NamePrefix,
            name: str
    ) -> None:
        cls.Mapper.Model.create(
            author=System.user,
            name=f'{prefix.value}_{name}',
            posts_ids=[post.post_id for post in posts],
        )

    @classmethod  # Not in use
    def create_default2(  # pragma: no cover
            cls,
            posts: list[PublicPostFormInterface | PersonalPostFormInterface],
            name: str
    ) -> None:
        if isinstance(posts[0], PublicPostForm):
            name = f'{Collection.NamePrefix.PUBLIC.value}_{name}'
        else:
            name = f'{Collection.NamePrefix.PERSONAL.value}_{name}'

        created_posts_ids = []
        for post in posts:
            created_posts_ids.append(post.create())
        cls.Mapper.Model.create(
            author=cls.user,
            name=name,
            posts_id=created_posts_ids,
        )

    @classmethod
    def get_by_ids(cls, ids: list[int], user: app.models.users.UserInterface, ) -> list[Mapper.ModelInterface]:
        collections = cls.Mapper.Model.get_by_ids(ids=ids, user=user, )
        cls.remove_prefixes(collections=collections, )
        return collections

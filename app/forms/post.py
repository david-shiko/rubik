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
from typing import TYPE_CHECKING, Type, Protocol
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import app.models.base.posts

if TYPE_CHECKING:
    import app.models.users


@dataclass
class PostFormProtocol(Protocol, ):
    author: app.models.users.User
    message_id: int
    collection_names: set[str]


@dataclass
class PostFormDC:
    author: app.models.users.User
    message_id: int
    collection_names: set[str] = field(default_factory=set, )


class PublicPostInterface(PostFormProtocol, ABC, ):

    Mapper: Type

    @abstractmethod
    def create(self, ) -> PublicPostInterface:
        ...


class PublicPost(PostFormDC, PublicPostInterface, ):
    @dataclass(slots=True, )
    class Mapper:
        PublicPost = app.models.posts.PublicPost

    def create(self, ) -> PublicPostInterface:
        post = self.Mapper.PublicPost.create(
            author=self.author,
            message_id=self.message_id,
        )
        return post


class PersonalPostInterface(PostFormProtocol, ABC, ):
    Mapper: Type
    MAX_COLLECTION_NAME_LEN: int

    @abstractmethod
    def create(self, ) -> PersonalPostInterface:
        ...


class PersonalPost(PostFormDC, PersonalPostInterface, ):
    @dataclass(slots=True, )
    class Mapper:
        PersonalPost = app.models.posts.PersonalPost
        Collection = app.models.collections.Collection

    MAX_COLLECTION_NAME_LEN = Mapper.Collection.MAX_NAME_LEN

    def create(self, ) -> PersonalPostInterface:
        post = self.Mapper.PersonalPost.create(
            author=self.author,
            message_id=self.message_id,
        )
        for name in self.collection_names:
            # Collection.create and not user.create_collection to reduce coupling, increase cohesion, and adhere SRP
            self.Mapper.Collection.create(name=name, posts_ids=[post.post_id], author=self.author, )
        return post

    def handle_collection_names(self, text: str) -> None:
        """Handle collection names got from user input"""
        for name in text.strip().split():
            self.collection_names.add(name[:app.models.collections.Collection.MAX_NAME_LEN], )

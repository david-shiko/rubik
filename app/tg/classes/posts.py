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
from enum import Enum
from abc import ABC, abstractmethod

import app.models.posts

if TYPE_CHECKING:
    import app.models.users


class PostBaseEmoji:  # Use enum
    MARK_VOTE = '🔹'
    POS_EMOJI: str  # Pos emoji is differ for all
    NEG_EMOJI = '👎'  # Neg emoji is common for all


class PublicPostEmoji(PostBaseEmoji):  # Use enum
    POS_EMOJI = '👍'


class PersonalPostEmoji(PostBaseEmoji):  # Use enum
    POS_EMOJI = '❤'
    LIKE = 'like'
    DISLIKE = 'dislike'


class PostsChannels(Enum):
    POSTS = -1001528324775  # Main posts source
    STORE = -1001764079241  # Store for posts (intermediate proxy place)
    POSTS_LINK = '@RubikLovePosts'  # Main posts source name


class BotPublicPostInterface(app.models.posts.PublicPostInterface, ABC):
    POS_EMOJI: str
    NEG_EMOJI: str

    @abstractmethod
    def send(self, recipient: int, ):
        ...


class BotPublicPost(
    app.models.posts.PublicPost,
    PublicPostEmoji,
    BotPublicPostInterface,
):
    ...

    def send(self, recipient: int, ):
        raise NotImplemented


class PublicPostInterface(app.models.posts.PublicPostInterface, ABC):

    POSTS_CHANNEL_ID: PostsChannels.POSTS.value  # Main posts source
    STORE_CHANNEL_ID: PostsChannels.STORE.value  # Store for posts (intermediate proxy place)

    @abstractmethod
    def send(self, recipient: int, ):
        ...


class PublicPost(
    app.models.posts.PublicPost,
    PublicPostEmoji,
    PublicPostInterface,
):
    POSTS_CHANNEL_ID = PostsChannels.POSTS.value  # Main posts source
    STORE_CHANNEL_ID = PostsChannels.STORE.value  # Store for posts (intermediate proxy place)

    def send(self, recipient: int, ):
        raise NotImplemented


class BotPersonalPostInterface(app.models.posts.PersonalPostInterface, ABC):
    POS_EMOJI: str
    NEG_EMOJI: str

    @abstractmethod
    def send(self, recipient: int, ):
        ...


class BotPersonalPost(
    app.models.posts.PersonalPost,
    PersonalPostEmoji,
    BotPersonalPostInterface,
):
    ...

    def send(self, recipient: int, ):
        raise NotImplemented


class PersonalPostInterface(ABC):

    @abstractmethod
    def send(
            self,
            clicker_vote: app.models.votes.PersonalVote,
            opposite_vote: app.models.votes.PersonalVote,
    ):
        ...

    @abstractmethod
    def share(
            self,
            post_sender: app.models.users.User,
            post_recipient: app.models.users.User,
    ) -> Exception | None:
        """Share post from one user to another (send the same post simultaneous;y to 2 users)"""
        ...


class PersonalPost(
    app.models.posts.PersonalPost,
    PersonalPostEmoji,
    PersonalPostInterface,
):
    STORE_CHANNEL_ID = PostsChannels.STORE.value

    @abstractmethod
    def send(
            self,
            clicker_vote: app.models.votes.PersonalVote,
            opposite_vote: app.models.votes.PersonalVote,
    ):
        raise NotImplemented

    @abstractmethod
    def share(
            self,
            post_sender: app.models.users.User,
            post_recipient: app.models.users.User,
    ) -> Exception | None:
        """Share post from one user to another (send the same post simultaneous;y to 2 users)"""
        raise NotImplemented


class VotedPublicPostInterface(app.models.posts.VotedPublicPostInterface, ABC, ):
    @abstractmethod
    def send(self):
        ...


class VotedPublicPost(
    app.models.posts.VotedPublicPost,
    VotedPublicPostInterface,
):
    def send(self):
        raise NotImplemented


class VotedPersonalPostInterface(app.models.posts.VotedPersonalPostInterface, ABC, ):
    @abstractmethod
    def send(self):
        ...


class VotedPersonalPost(
    app.models.posts.VotedPersonalPost,
    VotedPersonalPostInterface,
):
    def send(self):
        raise NotImplemented

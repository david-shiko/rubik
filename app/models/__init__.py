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
from typing import Type, Union

# # # # Base logic domains
import app.models.base.votes
import app.models.base.posts
import app.models.base.matches
import app.models.base.users
import app.models.base.collections

# # # Logic domains
from app.models import votes
from app.models import mix
from app.models import matches
from app.models import posts
from app.models import collections
from app.models import users


class Mapper:
    MapperModules = Union[
        Type[mix.Photo],
        Type[votes.PublicVote],
        Type[votes.PersonalVote],
        Type[posts.PublicPost],
        Type[posts.PersonalPost],
        Type[collections.Collection],
        Type[matches.Matcher],
        Type[users.User],
    ]

    @classmethod
    def set_mappers(cls):
        mix.Photo.Mapper = cls()
        votes.PublicVote.Mapper = PublicVoteMapper
        votes.PersonalVote.Mapper = PersonalVoteMapper
        posts.PublicPost.Mapper = PublicPostMapper
        posts.PersonalPost.Mapper = PersonalPostMapper
        collections.Collection.Mapper = CollectionMapper
        matches.Matcher.Mapper = MatcherMapper
        matches.Match.Mapper = MatchMapper
        users.User.Mapper = UserMapper


class UserMapper(Mapper):
    # post, vote?
    PublicVote = votes.PublicVote
    PersonalVote = votes.PersonalVote
    PublicPost = posts.PublicPost
    PersonalPost = posts.PersonalPost
    Collection = collections.Collection
    Matcher = matches.Matcher
    Photo = mix.Photo


class MatchMapper(Mapper):
    match = matches.Match


class MatcherMapper(Mapper):
    Match = matches.Match
    User = users.User


class CollectionMapper(Mapper):
    PublicPost = posts.PublicPost
    PersonalPost = posts.PersonalPost
    User = users.User


class PublicVoteMapper(Mapper):
    Post = posts.PublicPost


class PersonalVoteMapper(Mapper):
    Post = posts.PersonalPost


class PublicPostMapper(Mapper):
    Vote = votes.PublicVote
    User = users.User


class PersonalPostMapper(Mapper):
    Vote = votes.PersonalVote
    User = users.User


Mapper.set_mappers()

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
from typing import TYPE_CHECKING, Type, Union

import app.models
from app.tg.ptb.classes import votes, posts, collections, matches, users

if TYPE_CHECKING:
    pass


class Mapper(app.models.Mapper, ):
    MapperModules = Union[
        Type[votes.PublicVote],
        Type[votes.PersonalVote],
        Type[posts.PublicPost],
        Type[posts.PersonalPost],
        Type[posts.VotedPersonalPost],
        Type[collections.Collection],
        Type[matches.Matcher],
        Type[users.User],
    ]

    @classmethod
    def set_mappers(cls):
        votes.PublicVote.Mapper = PublicVoteMapper
        votes.PersonalVote.Mapper = PersonalVoteMapper
        posts.PublicPost.Mapper = PublicVoteMapper
        posts.PersonalPost.Mapper = PersonalPostMapper
        collections.Collection.Mapper = CollectionMapper
        matches.Matcher.Mapper = MatcherMapper
        matches.Match.Mapper = MatchMapper
        users.User.Mapper = UserMapper


class UserMapper(app.models.UserMapper, Mapper, ):
    # post, vote?
    PublicVote = votes.PublicVote
    PersonalVote = votes.PersonalVote
    PublicPost = posts.PublicPost
    PersonalPost = posts.PersonalPost
    Collection = collections.Collection
    Matcher = matches.Matcher


class MatcherMapper(app.models.MatcherMapper, Mapper, ):
    Match = matches.Match
    User = users.User


class MatchMapper(app.models.MatchMapper, Mapper, ):
    Match = matches.Match


class CollectionMapper(app.models.CollectionMapper, Mapper, ):
    PublicPost = posts.PublicPost
    PersonalPost = posts.PersonalPost
    User = users.User


class PublicVoteMapper(app.models.PublicVoteMapper, Mapper, ):
    Post = posts.PublicPost
    User = users.User
    Vote = votes.PublicVote


class PersonalVoteMapper(app.models.PersonalVoteMapper, Mapper, ):
    Post = posts.PersonalPost
    User = users.User
    Vote = votes.PersonalVote


class PublicPostMapper(app.models.PublicPostMapper, Mapper, ):
    Vote = votes.PersonalVote
    User = users.User


class PersonalPostMapper(app.models.PersonalPostMapper, Mapper, ):
    Vote = votes.PersonalVote


Mapper.set_mappers()

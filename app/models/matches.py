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
from typing import TYPE_CHECKING, Type

from app.models import base
import app.structures.base

if TYPE_CHECKING:
    from app.models import MatchMapper, MatcherMapper
    import app.models.users


class MatchInterface(base.matches.MatchInterface, ABC, ):
    Mapper: Type[MatchMapper]


class Match(base.matches.Match, MatchInterface, ):
    Mapper: Type[MatchMapper]


class MatcherInterface(base.matches.MatcherInterface, ABC, ):
    Mapper: Type[MatcherMapper]

    @abstractmethod
    def set_matches(self, ):
        ...

    @abstractmethod
    def convert_matches(self, raw_matches: list[app.structures.base.Covote], ) -> list[Match]:
        ...

    @abstractmethod
    def make_search(self, drop_old_votes: bool = False, drop_old_matches: bool = False, ) -> list[Match]:
        ...


class Matcher(base.matches.Matcher, MatcherInterface, ):
    """
    Order of search:
    1. read only user public votes.
    2. read unfiltered_covotes
    3. read filtered covotes
    """

    Mapper: Type[MatcherMapper]

    def set_matches(self, ):
        self.matches.all = self.convert_matches(raw_matches=self.matches.raw.all, )
        new_matches_ids = set(raw_match['id'] for raw_match in self.matches.raw.new)
        self.matches.new = [match for match in self.matches.all if match.id in new_matches_ids]
        self.matches.count_new = len(self.matches.new)
        self.matches.count_all = len(self.matches.all)

    def convert_matches(self, raw_matches: list[app.structures.base.Covote], ) -> list[Match]:
        result = []
        for raw_match in raw_matches:
            perc = self.get_common_interests_perc(common_posts_count=raw_match['count_common_interests'], )
            user = self.Mapper.User(tg_user_id=raw_match['tg_user_id'], )
            result.append(
                self.Mapper.Match(
                    id=raw_match['id'],
                    owner=self.user,
                    user=user,
                    common_posts_count=raw_match['count_common_interests'],
                    common_posts_perc=perc,
                )
            )
        return result

    def make_search(self, drop_old_votes: bool = False, drop_old_matches: bool = False, ) -> list[Match]:
        # Will be executed only if tables not exists
        super().make_search(drop_old_votes=drop_old_votes, drop_old_matches=drop_old_matches, )
        self.set_matches()
        return self.matches.all

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
from enum import IntEnum
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Protocol, TypedDict, Type
from dataclasses import dataclass, asdict, field
from pprint import pformat

from app.utils import get_perc

import app.db.crud.users
import app.structures.base

if TYPE_CHECKING:
    from datetime import datetime as datetime_datetime
    import app.models.base.users


class MatchInterface(ABC, ):
    CRUD: Type[app.db.crud.users.Match]

    class Stats(ABC, ):
        common_posts_count: int
        common_posts_perc: int

    @abstractmethod
    def __repr__(self, ) -> str:
        ...

    @abstractmethod
    def create(self, ) -> None:
        ...


class Match(MatchInterface, ):
    CRUD = app.db.crud.users.Match

    @dataclass()
    class Stats:
        common_posts_count: int
        common_posts_perc: int

    def __init__(
            self,
            id: int,
            owner: app.models.base.users.User,
            user: app.models.base.users.User,
            common_posts_count: int,
            common_posts_perc: int,
    ):
        self.id = id
        self.owner = owner  # User who get this match
        self.user = user
        self.stats = self.Stats(
            common_posts_count=common_posts_count,
            common_posts_perc=common_posts_perc,
        )

    def __repr__(self, ):
        d = {
            'self': object.__repr__(self, ),
            'tg_user_id': self.user.tg_user_id,
            'common_posts_count': self.stats.common_posts_count,
            'common_posts_perc': self.stats.common_posts_perc,
        }
        return repr({k: v for k, v in d.items() if v is not None}) + '\n'

    def create(self, ) -> None:
        return self.CRUD.create(
            tg_user_id=self.owner.tg_user_id,
            matched_tg_user_id=self.user.tg_user_id,
            connection=self.owner.connection,
        )


class MatcherDCProtocol(Protocol, ):
    class Limit(Protocol):
        min: int
        average: int

    class Filters(ABC):
        Goal: app.structures.base.Goal

        class Gender(IntEnum):
            MALE: app.structures.base.Gender.MALE
            FEMALE: app.structures.base.Gender.FEMALE
            BOTH: int

        Age: app.structures.base.Age

        class Checkbox(TypedDict):
            age: bool
            photo: bool
            country: bool
            city: bool

        checkboxes: Checkbox
        gender: Gender
        goal: app.structures.base.Goal
        age_range: tuple[MatcherDCProtocol.Filters.Age.MIN, Age.MAX]

    class MatchesRaw(ABC, ):
        covotes: list[app.structures.base.Covote]
        unfiltered: list[app.structures.base.Covote]
        new: list[app.structures.base.Covote]
        all: list[app.structures.base.Covote]
        current: list[app.structures.base.Covote]
        count_all: int | None
        count_new: int | None

        @abstractmethod
        def __repr__(self) -> str:
            ...

    class Matches(ABC):
        raw: MatcherDCProtocol.MatchesRaw
        covotes: list[MatchInterface]
        unfiltered: list[MatchInterface]
        new: list[MatchInterface]
        all: list[MatchInterface]
        current: list[MatchInterface]
        count_all: int | None
        count_new: int | None

    class SearchResult(ABC):  # Use me
        id: int
        filters: MatcherDCProtocol.Filters
        matches: MatcherDCProtocol.Matches
        datetime: datetime_datetime

    CRUD: app.db.crud.users.Matcher


class MatcherInterface(MatcherDCProtocol, ):

    @abstractmethod
    def __repr__(self, ) -> str:
        ...

    @abstractmethod
    def drop_votes_table(self, ) -> None:
        ...

    @abstractmethod
    def drop_matches_table(self, ) -> None:
        ...

    @abstractmethod
    def create_user_votes(self, ) -> None:
        ...

    @abstractmethod
    def create_user_covotes(self, ) -> None:
        ...

    @abstractmethod
    def get_user_votes(self, ) -> list[app.structures.base.UserPublicVote]:
        ...

    @abstractmethod
    def get_user_matches(self, new: bool = False) -> list[app.structures.base.Covote]:
        ...

    @abstractmethod
    def create_unfiltered_matches(self, drop_old_votes: bool = False, drop_old_matches: bool = False) -> None:
        ...

    @abstractmethod
    def apply_goal_filter(self, update: bool = False):
        ...

    @abstractmethod
    def apply_gender_filter(self, update: bool = False):
        ...

    @abstractmethod
    def apply_age_filter(self, update: bool = False):
        ...

    @abstractmethod
    def apply_checkboxes_country_filter(self, update: bool = False):
        ...

    @abstractmethod
    def apply_checkboxes_city_filter(self, update: bool = False):
        ...

    @abstractmethod
    def apply_checkboxes_photo_filter(self, update: bool = False):
        ...

    @abstractmethod
    def filter_matches(self, update: bool = False) -> None:
        ...

    @abstractmethod
    def set_matches_raw(self, ):
        ...

    @abstractmethod
    def set_current_matches(self, ):
        ...

    @abstractmethod
    def get_common_interests_perc(self, common_posts_count: int, ) -> int:
        ...

    @abstractmethod
    def get_match(self, pop: bool = True) -> Match | None:
        ...


@dataclass
class MatcherDC(MatcherDCProtocol):

    class Limit(IntEnum, ):  # Use me
        min: int = 1
        average: int = 10

    @dataclass
    class Filters:
        Goal = app.structures.base.Goal

        class Gender(IntEnum):
            MALE = app.structures.base.Gender.MALE.value
            FEMALE = app.structures.base.Gender.FEMALE.value
            BOTH = 3

        Age = app.structures.base.Age

        class Checkbox(TypedDict, ):
            age: bool
            photo: bool
            country: bool
            city: bool

        class Checkboxes(dict, ):
            def __init__(
                    self,
                    age: bool = True,
                    photo: bool = False,
                    country: bool = False,
                    city: bool = False
            ) -> None:
                super().__init__(age=age, photo=photo, country=country, city=city)

        class MatchType(IntEnum, ):
            ALL_MATCHES = 1
            NEW_MATCHES = 2

        gender = Gender.BOTH
        goal = app.structures.base.Goal.BOTH
        age_range: tuple = (Age.MIN, Age.MAX,)
        match_type: MatchType = MatchType.ALL_MATCHES
        checkboxes: Checkboxes = field(default_factory=lambda: MatcherDC.Filters.Checkboxes())

    @dataclass
    class SearchResult:  # Use it
        id: int
        filters: Matcher.Filters
        matches: Matcher.Matches
        datetime: datetime_datetime

    @dataclass
    class MatchesRaw:
        all: list[app.structures.base.Covote] = field(default_factory=list, )
        new: list[app.structures.base.Covote] = field(default_factory=list, )  # new is one of filters
        current: list[app.structures.base.Covote] = field(default_factory=list, )
        count_all: int = 0
        count_new: int = 0

    class Matches:  # No dataclass cuz field(default_factory=Matcher.MatchesRaw()) not aware about MatchesRaw cls
        def __init__(self, ):
            self.raw: Matcher.MatchesRaw = Matcher.MatchesRaw()
            self.new: list[Match] = []
            self.all: list[Match] = []
            self.current: list[Match] = []
            self.count_all: int = 0
            self.count_new: int = 0


class Matcher(MatcherDC, MatcherInterface, ):
    """
    Order of search:
    1. read only user public votes.
    2. read unfiltered_covotes
    3. read filtered covotes
    """

    CRUD = app.db.crud.users.Matcher

    def __init__(self, user: app.models.base.users.User, filters: MatcherDC.Filters | None = None, ):
        self.user = user
        self.filters = filters or self.Filters()
        self.matches = self.Matches()
        self.user_votes_count = 0
        self.is_user_has_votes = False
        self.is_user_has_covotes = False
        self.search_results: list[Matcher.SearchResult] = []  # Not in use
        self._is_unfiltered_matches_already_set = False  # tmp solution

    def __repr__(self, ):
        d = {
            'self': object.__repr__(self, ),
            'user': self.user,
            'matches': self.matches,
            'target': self.filters,
        }
        return repr({k: v for k, v in d.items() if v is not None}) + '\n'

    # Not in use, use me
    def is_user_has_enough_votes(self, limit: Matcher.Limit, ) -> bool:  # pragma: no cover
        return self.user_votes_count > limit.value

    def drop_votes_table(self, ) -> None:
        """Drop a table (user_votes) if you need completely new search (reselect user votes"""
        return self.CRUD.drop_votes_table(connection=self.user.connection, )

    def drop_matches_table(self, ) -> None:
        """Drop a table (user_covotes) if you need make search with new filters"""
        return self.CRUD.drop_matches_table(connection=self.user.connection, )

    def create_user_votes(self, ) -> None:
        """Caching, collect user votes in temporary table to increase performance"""
        # [#1] Raise if no votes?
        self.CRUD.create_user_votes(tg_user_id=self.user.tg_user_id, connection=self.user.connection, )

    def create_user_covotes(self, ) -> None:
        """Caching, collect user covotes in temporary table to increase performance"""
        # [#2] Raise if no covotes?
        # Will be executed only if table not exists
        self.create_user_votes()  # Next query depend on this table
        self.CRUD.create_user_covotes(tg_user_id=self.user.tg_user_id, connection=self.user.connection, )

    def get_user_votes(self, ) -> list[app.structures.base.UserPublicVote]:
        """
        Will create a temporary table with user votes
        There an option to select only one vote for checking
        but most likely in next steps will need to select rest votes
        """
        result = self.CRUD.read_user_votes(connection=self.user.connection, )  # ID inside the connection
        return result

    def get_user_matches(self, new: bool = False, ) -> list[app.structures.base.Covote]:
        """Will create a temporary table with user covotes"""
        return self.CRUD.read_user_covotes(
            tg_user_id=self.user.tg_user_id,
            connection=self.user.connection,
            new=new,
        )

    def create_unfiltered_matches(self, drop_old_votes: bool = False, drop_old_matches: bool = False, ) -> None:
        if drop_old_votes:  # Dropping old_votes also drops old_matches ?? (check it)
            self.drop_votes_table()
        if drop_old_matches:
            self.drop_matches_table()
        self.create_user_votes()  # Will be executed only if table not exists
        self.user_votes_count = self.CRUD.read_user_votes_count(connection=self.user.connection, )
        self.is_user_has_votes = bool(self.user_votes_count)
        if self.user_votes_count:
            self.create_user_covotes()  # Will be executed only if table not exists
            self.is_user_has_covotes = bool(self.CRUD.read_user_covotes_count(connection=self.user.connection, ))
        self._is_unfiltered_matches_already_set = True

    def apply_goal_filter(self, update: bool = False, ):
        if self.filters.goal != self.Filters.Goal.BOTH:
            self.CRUD.apply_goal_filter(goal=self.filters.goal.value, connection=self.user.connection, )
            if update is True:
                self.matches.raw.current = self.get_user_matches()  # Update data

    def apply_gender_filter(self, update: bool = False, ):
        if self.filters.gender != self.Filters.Gender.BOTH:
            self.CRUD.apply_gender_filter(gender=self.filters.gender.value, connection=self.user.connection, )
            if update is True:
                self.matches.raw.current = self.get_user_matches()  # Update data

    def apply_age_filter(self, update: bool = False, ):
        if self.filters.age_range != tuple(self.Filters.Age):
            self.CRUD.apply_age_filter(
                min_age=self.filters.age_range[0],
                max_age=self.filters.age_range[1],
                connection=self.user.connection,
            )
            if update is True:
                self.matches.raw.current = self.get_user_matches()  # Update data

    def apply_checkboxes_country_filter(self, update: bool = False, ):
        if self.filters.checkboxes['country']:
            self.CRUD.apply_checkboxes_country_filter(connection=self.user.connection, )
            if update is True:
                self.matches.raw.current = self.get_user_matches()  # Update data

    def apply_checkboxes_city_filter(self, update: bool = False, ):
        if self.filters.checkboxes['city']:
            self.CRUD.apply_checkboxes_city_filter(connection=self.user.connection, )
            if update is True:
                self.matches.raw.current = self.get_user_matches()  # Update data

    def apply_checkboxes_photo_filter(self, update: bool = False, ):
        if self.filters.checkboxes['photo']:
            self.CRUD.apply_checkboxes_photo_filter(connection=self.user.connection, )
            if update is True:
                self.matches.raw.current = self.get_user_matches()  # Update data

    def filter_matches(self, update: bool = False) -> None:
        # TODO Set restriction if filters are the same
        self.apply_goal_filter()
        self.apply_gender_filter()
        self.apply_age_filter()
        self.apply_checkboxes_country_filter()
        self.apply_checkboxes_city_filter()
        self.apply_checkboxes_photo_filter()
        if update is True:
            self.matches.raw.current = self.get_user_matches()  # Update data

    def set_matches_raw(self, ) -> None:
        self.matches.raw.new = self.get_user_matches(new=True, )
        self.matches.raw.all = self.get_user_matches(new=False, )
        # Convert 'new' to a dictionary for faster lookup
        new_dict = {covote['id']: covote for covote in self.matches.raw.new}
        # Replace duplicates with a references to new items
        self.matches.raw.all = [new_dict.get(item['id'], item) for item in self.matches.raw.all]
        self.matches.raw.count_new = len(self.matches.raw.new)
        self.matches.raw.count_all = len(self.matches.raw.all)

    def set_current_matches(self, ) -> None:
        if self.filters.match_type == self.Filters.MatchType.ALL_MATCHES:
            self.matches.current = self.matches.all
        elif self.filters.match_type == self.Filters.MatchType.NEW_MATCHES:
            self.matches.current = self.matches.new

    def get_common_interests_perc(self, common_posts_count: int, ) -> int:
        return get_perc(num_1=common_posts_count, num_2=self.user_votes_count, )

    def make_search(
            self,
            drop_old_votes: bool = False,
            drop_old_matches: bool = False,
    ) -> list[app.structures.base.Covote]:
        """Matches base may return only raw obj final obj contain user attr"""
        if self._is_unfiltered_matches_already_set is False:  # A bit dirty tmp solution
            self.create_unfiltered_matches(drop_old_votes=drop_old_votes, drop_old_matches=drop_old_matches, )
        self.filter_matches()
        self.set_matches_raw()
        return self.matches.raw.all

    def get_match(self, pop: bool = True, ) -> Match | None:
        if self.matches.current:
            if pop:
                return self.matches.current.pop()
            else:
                return self.matches.current[-1]
        return None

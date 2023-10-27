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

from app.models import mix
import app.models.matches  # Models layer is cuz tg matches not exists

if TYPE_CHECKING:
    from app.tg import ptb
    from app.tg.ptb.classes.users import UserInterface


class MatchInterface(app.models.matches.MatchInterface, ABC, ):
    Mapper: Type[ptb.classes.MatchMapper]

    @abstractmethod
    def show(self) -> None:
        ...


class Match(app.models.matches.Match, MatchInterface, ):
    Mapper: Type[ptb.classes.MatchMapper]

    def show(self, ) -> None:
        self.user.profile.send(self.owner.tg_user_id, )
        self.create()  # Save shown match to db


class MatcherInterface(app.models.matches.MatcherInterface, ABC, ):
    Mapper: Type[ptb.classes.MatcherMapper]


class Matcher(app.models.matches.Matcher, MatcherInterface, ):
    Mapper: Type[ptb.classes.MatcherMapper]

    def convert_matches(self, raw_matches: list[app.structures.base.Covote], ) -> list[Match]:
        matches = super().convert_matches(raw_matches=raw_matches, )
        for match in matches:
            match.user.profile.is_loaded = False  # Quickfix
        return matches


class MatchStatsProtocol(mix.MatchStatsProtocol, ABC, ):
    user: UserInterface


class MatchStatsInterface(mix.MatchStatsInterface, MatchStatsProtocol, ABC, ):
    ...


class MatchStats(mix.MatchStats, MatchStatsInterface, ):
    ...

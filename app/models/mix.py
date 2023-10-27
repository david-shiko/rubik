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
from typing import TYPE_CHECKING, Union, Protocol
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from io import BytesIO

import matplotlib.pyplot as plt

import app.structures.base
from app.utils import get_perc, limit_num
from app.db import crud

if TYPE_CHECKING:
    from app.models.users import UserInterface
    from app.structures.base import PersonalVotesStatsDB


class MatchStatsProtocol(Protocol):
    user: UserInterface
    with_tg_user_id: int
    pos_votes_count: int | None
    neg_votes_count: int | None
    zero_votes_count: int | None
    opposite_pos_votes_count: int | None
    opposite_neg_votes_count: int | None
    opposite_zero_votes_count: int | None
    common_pos_votes_perc: int | None
    common_neg_votes_perc: int | None
    common_zero_votes_perc: int | None


class MatchStatsInterface(MatchStatsProtocol, ABC, ):

    @abstractmethod
    def __init__(self, user: UserInterface, with_tg_user_id: int, set_statistic: bool = True, ) -> None:
        pass

    @staticmethod
    @abstractmethod
    def get_common_votes_perc(num_with_votes: Union[int, None], num_my_votes: int) -> int:
        pass

    @abstractmethod
    def read_user_personal_votes_statistic(
            self,
            tg_user_id: Union[int, None] = None
    ) -> PersonalVotesStatsDB:
        pass

    @abstractmethod
    def set_statistic_v1(self) -> None:
        pass

    @abstractmethod
    def set_statistic_v2(self) -> None:
        pass

    @abstractmethod
    def set_statistic(self, version: int, ):
        pass

    @abstractmethod
    def fill_stats(
            self,
            personal_votes_stats: PersonalVotesStatsDB,
            opposite_covotes_stats: PersonalVotesStatsDB
    ) -> None:
        pass

    @abstractmethod
    def fill_random(self) -> None:
        pass

    @abstractmethod
    def get_pie_chart_result(self) -> BytesIO:
        pass


@dataclass
class VotesStats:
    """
    "pos_votes_count" - Just count of my personal votes
    "neg_votes_count" - Just count of my personal votes
    "zero_votes_count" - Just count of my personal votes
    "opposite_pos_votes_count" - count of another personal user COVOTES with me
    "opposite_neg_votes_count" - count of another personal user COVOTES with me
    "opposite_zero_votes_count" - count of another personal user COVOTES with me
    "common_pos_votes_perc" - percentage of another personal user COVOTES with me (the same as "with_*" but in %)
    "common_neg_votes_perc" - percentage of another personal user COVOTES with me (the same as "with_*" but in %)
    "common_zero_votes_perc" - percentage of another personal user COVOTES with me (the same as "with_*" but in %)
    """
    pos_votes_count: int | None = None
    neg_votes_count: int | None = None
    zero_votes_count: int | None = None
    opposite_pos_votes_count: int | None = None
    opposite_neg_votes_count: int | None = None
    opposite_zero_votes_count: int | None = None
    common_pos_votes_perc: int | None = None
    common_neg_votes_perc: int | None = None
    common_zero_votes_perc: int | None = None

    def __init__(self):  # Is it a good practice?
        self.__dict__ = asdict(self)  # Use __iter__ to apply dict() on self


class MatchStats(VotesStats, ):
    CRUD = crud.mix.MatchStats

    def __init__(self, user: UserInterface, with_tg_user_id: int, set_statistic: bool = True, ):
        super().__init__()
        self.user = user
        self.with_tg_user_id = with_tg_user_id
        if set_statistic is True:
            self.set_statistic()

    @staticmethod
    def get_common_votes_perc(num_with_votes: int | None, num_my_votes: int, ) -> int:
        result = get_perc(num_1=num_with_votes, num_2=num_my_votes, )
        if result > 100:
            return 100
        return result

    def read_user_personal_votes_statistic(
            self,
            tg_user_id: int | None = None,
    ) -> app.structures.base.PersonalVotesStatsDB:
        """Func to fill parameters with self mainly"""
        user_personal_votes_statistic = self.CRUD.read_user_personal_votes_statistic(
            tg_user_id=tg_user_id or self.user.tg_user_id,
            connection=self.user.connection,
        )
        return user_personal_votes_statistic

    def set_statistic_v1(self, ) -> None:  # Make separate class
        self.CRUD.drop_temp_table_user_personal_votes(connection=self.user.connection, )
        self.CRUD.create_temp_table_personal_votes(tg_user_id=self.user.tg_user_id, connection=self.user.connection, )
        personal_votes_statistic = self.CRUD.read_user_personal_votes_statistic(
            tg_user_id=self.user.tg_user_id,
            connection=self.user.connection,
        )  # Will cause error !
        opposite_covotes_stats = self.CRUD.read_personal_covotes_count(
            tg_user_id=self.user.tg_user_id,
            connection=self.user.connection,
        )
        self.fill_stats(personal_votes_stats=personal_votes_statistic, opposite_covotes_stats=opposite_covotes_stats)

    def set_statistic_v2(self, ) -> None:  # Make separate class
        # Create my_personal_votes table for every user and get from it?
        self.CRUD.drop_temp_table_my_and_covote_personal_votes(connection=self.user.connection, )
        self.CRUD.create_temp_table_my_and_covote_personal_votes(
            tg_user_id=self.user.tg_user_id,
            with_tg_user_id=self.with_tg_user_id,
            connection=self.user.connection,
        )
        self.fill_stats(
            personal_votes_stats=self.read_user_personal_votes_statistic(),
            opposite_covotes_stats=self.read_user_personal_votes_statistic(tg_user_id=self.with_tg_user_id, ),
        )

    def set_statistic(self, version: int = 2, ):
        if version == 1:
            self.set_statistic_v1()
        elif version == 2:
            self.set_statistic_v2()

    def fill_stats(
            self,
            personal_votes_stats: app.structures.base.PersonalVotesStatsDB,
            opposite_covotes_stats: app.structures.base.PersonalVotesStatsDB,
    ) -> None:
        self.pos_votes_count: int = personal_votes_stats['num_pos_votes']
        self.neg_votes_count: int = personal_votes_stats['num_neg_votes']
        self.zero_votes_count: int = personal_votes_stats['num_zero_votes']
        self.opposite_pos_votes_count: int = opposite_covotes_stats['num_pos_votes']
        self.opposite_neg_votes_count: int = opposite_covotes_stats['num_neg_votes']
        self.opposite_zero_votes_count: int = opposite_covotes_stats['num_zero_votes']
        self.common_pos_votes_perc: int = self.get_common_votes_perc(
            num_with_votes=self.opposite_pos_votes_count,
            num_my_votes=self.pos_votes_count,
        )
        self.common_neg_votes_perc = self.get_common_votes_perc(
            num_with_votes=self.opposite_neg_votes_count,
            num_my_votes=self.neg_votes_count,
        )
        self.common_zero_votes_perc = self.get_common_votes_perc(
            num_with_votes=self.opposite_zero_votes_count,
            num_my_votes=self.zero_votes_count,
        )

    def fill_random(self, ) -> None:
        my_stats = app.structures.base.PersonalVotesStatsDB(
            num_pos_votes=100,
            num_neg_votes=50,
            num_zero_votes=20,
        )
        opposite_stats = app.structures.base.PersonalVotesStatsDB(
            num_pos_votes=80,
            num_neg_votes=40,
            num_zero_votes=5,
        )
        self.fill_stats(personal_votes_stats=my_stats, opposite_covotes_stats=opposite_stats)

    def get_pie_chart_result(self, ) -> BytesIO:
        values = [self.pos_votes_count, self.neg_votes_count, self.zero_votes_count]
        iter_values = iter(values)
        labels = ['likes', 'dislikes', 'skipped']
        # "autotexts" will only be returned if the parameter autopct is not None.
        fontsize = 20
        patches, texts, autotexts = plt.pie(
            x=values,
            labels=labels,
            startangle=-10,  # Rotate circle to prevent label overlapping with aside summary (legend)
            wedgeprops={"edgecolor": "black", 'linewidth': 5, 'antialiased': True},  # Styles of circle itself
            # Numbers on the chart, ":d" - digit, ":.0f" - float with zero digits after a dot
            autopct=lambda float_percentage: '{:d} ({:.0f}%)'.format(next(iter_values), float_percentage),
            textprops={'color': "white", 'fontsize': fontsize, },  # Styles of numbers on the chart
            # Workaround to place labels inside the chart
            # autopct=lambda percentage: '{:s}\n{:d} ({:.0f}%)'.format(next(labels), next(values), percentage),
        )
        percentages = []
        total = sum(values)
        for i, x in enumerate(autotexts):
            percentage = get_perc(values[i], total)
            percentages.append(percentage)
            fontsize = limit_num(num=fontsize, min_num=15, max_num=25)
            # If num > 25^ autotexts[i].set_horizontalalignment('left')
            autotexts[i].set_fontsize(fontsize)  # Set font_size relative to size of chart item
            texts[i].set_color('black')  # Reset color for labels (was affected by "textprops")
        labels_ = [f'{label} - {percentage}%' for label, percentage in zip(labels, percentages)]
        # Place summary aside of chart
        plt.legend(handles=patches, labels=labels_, loc='upper center', bbox_to_anchor=(0, 1.1), fontsize=15)
        plt.tight_layout()  # Something useful ...
        buffer = BytesIO()
        plt.savefig(buffer, format='png', )
        buffer.seek(0)  # Required ?
        return buffer


class Photo:
    CRUD = crud.mix.Photo

    @classmethod
    def create(cls, user: UserInterface, photo: str) -> None:
        return cls.CRUD.create(tg_user_id=user.tg_user_id, photo=photo, connection=user.connection, )

    @classmethod
    def read(cls, user: UserInterface, ) -> list[str]:
        result = cls.CRUD.read(tg_user_id=user.tg_user_id, connection=user.connection, )
        return result

    @classmethod
    def delete_user_photos(cls, user: UserInterface, ) -> None:
        return cls.CRUD.delete_user_photos(tg_user_id=user.tg_user_id, connection=user.connection, )

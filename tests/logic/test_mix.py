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
from unittest.mock import patch
from io import BytesIO  # For isinstance checking
from collections import defaultdict

from app.models.mix import MatchStats, VotesStats, Photo

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from app.models.users import User


class TestMatchStats:
    @staticmethod
    def test_init(user_s: User, ):
        with_tg_user_id = 123  # Example id, replace it with your actual id
        with patch.object(MatchStats, 'set_statistic', autospec=True, ) as mock_set_statistic:
            match_stats = MatchStats(user_s, with_tg_user_id)
        assert match_stats.user == user_s
        assert match_stats.with_tg_user_id == with_tg_user_id
        mock_set_statistic.assert_called_once()

    @staticmethod
    def test_get_common_votes_perc(match_stats: MatchStats, ):
        assert match_stats.get_common_votes_perc(num_with_votes=10, num_my_votes=20) == 50
        assert match_stats.get_common_votes_perc(num_with_votes=20, num_my_votes=10) == 100
        assert match_stats.get_common_votes_perc(num_with_votes=3, num_my_votes=10) == 30
        assert match_stats.get_common_votes_perc(num_with_votes=100, num_my_votes=0) == 0
        assert match_stats.get_common_votes_perc(num_with_votes=0, num_my_votes=20) == 0

    @staticmethod
    def test_fill_stats(mock_match_stats: MagicMock, match_stats: MatchStats, ):
        # Assert not filled
        for k in vars(VotesStats()):  # Every key is None
            assert getattr(mock_match_stats, k) not in (0, mock_match_stats.get_common_votes_perc.return_value)
        # Execution
        d = defaultdict(int)
        MatchStats.fill_stats(
            self=mock_match_stats,
            personal_votes_stats=d,
            opposite_covotes_stats=d,
        )
        # Checks
        for k in vars(VotesStats()):  # Assert filled
            assert getattr(mock_match_stats, k) in (0, mock_match_stats.get_common_votes_perc.return_value)

    @staticmethod
    def test_read_user_personal_votes_statistic(mock_match_stats: MagicMock, ):
        result = MatchStats.read_user_personal_votes_statistic(self=mock_match_stats, )
        mock_match_stats.CRUD.read_user_personal_votes_statistic.assert_called_once_with(
            tg_user_id=mock_match_stats.user.tg_user_id,
            connection=mock_match_stats.user.connection,
        )
        assert result == mock_match_stats.CRUD.read_user_personal_votes_statistic.return_value

    @staticmethod
    def test_set_statistic_v1(mock_match_stats: MagicMock, ):
        MatchStats.set_statistic_v1(self=mock_match_stats, )
        # Checks
        mock_match_stats.CRUD.drop_temp_table_user_personal_votes(connection=mock_match_stats.user.connection, )
        mock_match_stats.CRUD.create_temp_table_personal_votes(
            tg_user_id=mock_match_stats.user.tg_user_id,
            connection=mock_match_stats.user.connection,
        )
        mock_match_stats.CRUD.read_user_personal_votes_statistic.assert_called_once_with(
            tg_user_id=mock_match_stats.user.tg_user_id,
            connection=mock_match_stats.user.connection,
        )
        mock_match_stats.CRUD.read_personal_covotes_count(
            tg_user_id=mock_match_stats.user.tg_user_id,
            connection=mock_match_stats.user.connection,
        )
        mock_match_stats.fill_stats.assert_called_once_with(
            personal_votes_stats=mock_match_stats.CRUD.read_user_personal_votes_statistic.return_value,
            opposite_covotes_stats=mock_match_stats.CRUD.read_personal_covotes_count.return_value,
        )

    @staticmethod
    def test_set_statistic_v2(mock_match_stats: MagicMock, ):
        self = mock_match_stats
        MatchStats.set_statistic_v2(self=mock_match_stats, )
        mock_match_stats.CRUD.drop_temp_table_my_and_covote_personal_votes.assert_called_once_with(
            connection=self.user.connection,
        )
        mock_match_stats.CRUD.create_temp_table_my_and_covote_personal_votes.assert_called_once_with(
            tg_user_id=self.user.tg_user_id,
            with_tg_user_id=self.with_tg_user_id,
            connection=self.user.connection,
        )
        self.fill_stats.assert_called_once_with(
            personal_votes_stats=self.read_user_personal_votes_statistic.return_value,
            opposite_covotes_stats=self.read_user_personal_votes_statistic.return_value
        )

    @staticmethod
    def test_set_statistic(mock_match_stats: MagicMock, ):
        MatchStats.set_statistic(self=mock_match_stats, version=1)
        MatchStats.set_statistic(self=mock_match_stats, version=2)
        mock_match_stats.set_statistic_v1.assert_called_once_with()
        mock_match_stats.set_statistic_v2.assert_called_once_with()

    @staticmethod
    def test_fill_random(match_stats: MatchStats, ) -> None:
        # Iterate over attr that are common for DC and cls(DC)
        assert all([getattr(match_stats, k) is None for k in vars(VotesStats())])
        # Execution
        assert match_stats.fill_random() is None
        # Checks
        assert match_stats.pos_votes_count == 100
        assert match_stats.neg_votes_count == 50
        assert match_stats.zero_votes_count == 20
        assert match_stats.opposite_pos_votes_count == 80
        assert match_stats.opposite_neg_votes_count == 40
        assert match_stats.opposite_zero_votes_count == 5
        assert match_stats.common_pos_votes_perc == 80
        assert match_stats.common_neg_votes_perc == 80
        assert match_stats.common_zero_votes_perc == 25

    @staticmethod
    def test_get_pie_chart_result(match_stats: MatchStats):
        # TODO need more tests
        match_stats.fill_random()  # To avoid None. TODO user fixture.
        result = match_stats.get_pie_chart_result()
        assert isinstance(result, BytesIO)


class TestPhoto:
    @staticmethod
    def test_create(user_s: User, ):
        with patch.object(Photo, 'CRUD', autospec=True, ) as mock_crud:
            Photo.create(user=user_s, photo='foo', )
        mock_crud.create.assert_called_once_with(
            tg_user_id=user_s.tg_user_id,
            photo='foo',
            connection=user_s.connection,
        )

    @staticmethod
    def test_read(user_s: User, ):
        with patch.object(Photo, 'CRUD', autospec=True, ) as mock_crud:
            result = Photo.read(user=user_s, )
        mock_crud.read.assert_called_once_with(
            tg_user_id=user_s.tg_user_id,
            connection=user_s.connection,
        )
        assert result == mock_crud.read.return_value

    @staticmethod
    def test_delete_user_photos(user_s: User, ):
        with patch.object(Photo, 'CRUD', autospec=True, ) as mock_crud:
            Photo.delete_user_photos(user=user_s, )
        mock_crud.delete_user_photos.assert_called_once_with(
            tg_user_id=user_s.tg_user_id,
            connection=user_s.connection,
        )

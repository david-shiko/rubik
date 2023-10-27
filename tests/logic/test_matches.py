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

from unittest.mock import patch, call, ANY
from typing import TYPE_CHECKING

import pytest

import app.models.base.matches
from app.models.matches import Match, Matcher
import app.tg.ptb.config

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from app.structures.base import Covote


class TestMatcher:
    @staticmethod
    def test_repr(matcher: Matcher, ):
        assert matcher.__repr__()

    @staticmethod
    def test_drop_votes_table(mock_matcher: app.models.matches.Matcher, ):
        app.models.matches.Matcher.drop_votes_table(self=mock_matcher, )
        mock_matcher.CRUD.drop_votes_table.assert_called_once_with(connection=mock_matcher.user.connection, )

    @staticmethod
    def test_drop_matches_table(mock_matcher: app.models.matches.Matcher, ):
        app.models.matches.Matcher.drop_matches_table(self=mock_matcher, )
        mock_matcher.CRUD.drop_matches_table.assert_called_once_with(connection=mock_matcher.user.connection, )

    @staticmethod
    def test_create_user_votes(mock_matcher: MagicMock, ):
        Matcher.create_user_votes(self=mock_matcher, )

    @staticmethod
    def test_create_user_covotes(mock_matcher: MagicMock, ):
        Matcher.create_user_covotes(self=mock_matcher, )

    @staticmethod
    def test_get_user_votes(mock_matcher: MagicMock, ):
        result = app.models.matches.Matcher.get_user_votes(self=mock_matcher, )
        # Checks
        mock_matcher.CRUD.read_user_votes.assert_called_once_with(connection=mock_matcher.user.connection, )
        assert result == mock_matcher.CRUD.read_user_votes.return_value

    @staticmethod
    def test_get_user_covotes_all(mock_matcher: MagicMock, ):
        result = app.models.matches.Matcher.get_user_matches(self=mock_matcher, )
        # Checks
        mock_matcher.CRUD.read_user_covotes.assert_called_once_with(
            tg_user_id=mock_matcher.user.tg_user_id,
            connection=mock_matcher.user.connection,
            new=ANY,
        )
        assert result == mock_matcher.CRUD.read_user_covotes.return_value

    @staticmethod
    def test_set_unfiltered_matches(
            mock_matcher: MagicMock,
    ):
        app.models.matches.Matcher.create_unfiltered_matches(
            self=mock_matcher,
            drop_old_votes=True,
            drop_old_matches=True,
        )
        mock_matcher.drop_votes_table.assert_called_once_with()
        mock_matcher.drop_matches_table.assert_called_once_with()
        mock_matcher.create_user_votes.assert_called_once_with()
        mock_matcher.CRUD.read_user_votes_count.assert_called_once_with(connection=mock_matcher.user.connection, )
        mock_matcher.create_user_covotes.assert_called_once_with()
        mock_matcher.CRUD.read_user_covotes_count.assert_called_once_with(connection=mock_matcher.user.connection, )
        assert mock_matcher.is_user_has_covotes is True

    @staticmethod
    @pytest.mark.parametrize(
        argnames='goal',
        argvalues=(Matcher.Filters.Goal.CHAT, Matcher.Filters.Goal.DATE,),
    )
    def test_apply_goal_filter(mock_matcher: MagicMock, goal: Matcher.Filters.Goal, ):
        mock_matcher.filters.goal = goal
        Matcher.apply_goal_filter(self=mock_matcher, update=True, )
        mock_matcher.CRUD.apply_goal_filter.assert_called_once_with(
            goal=mock_matcher.filters.goal.value,
            connection=mock_matcher.user.connection,
        )
        mock_matcher.get_user_matches.assert_called_once_with()
        assert mock_matcher.matches.raw.current == mock_matcher.get_user_matches.return_value

    @staticmethod
    def test_apply_goal_filter_both(mock_matcher: MagicMock, ):
        """Check that filter was not applied and no any changes"""
        mock_matcher.filters.goal = mock_matcher.Filters.Goal.BOTH
        Matcher.apply_goal_filter(self=mock_matcher, update=True, )
        mock_matcher.CRUD.apply_goal_filter.assert_not_called()

    @staticmethod
    @pytest.mark.parametrize(
        argnames='gender',
        argvalues=(Matcher.Filters.Gender.MALE, Matcher.Filters.Gender.FEMALE,),
    )
    def test_apply_gender_filter(mock_matcher: MagicMock, monkeypatch, gender: Matcher.Filters.Gender, ):
        """Check that filter was not applied and no any changes"""
        monkeypatch.setattr(mock_matcher.filters, 'gender', gender, )
        Matcher.apply_gender_filter(self=mock_matcher, update=True, )
        mock_matcher.CRUD.apply_gender_filter.assert_called_once_with(
            gender=mock_matcher.filters.gender.value,
            connection=mock_matcher.user.connection,
        )
        mock_matcher.get_user_matches.assert_called_once_with()
        assert mock_matcher.matches.raw.current == mock_matcher.get_user_matches.return_value

    @staticmethod
    def test_apply_gender_filter_both(mock_matcher: MagicMock, ):
        """Check that filter was not applied and no any changes"""
        mock_matcher.filters.gender = mock_matcher.Filters.Gender.BOTH
        Matcher.apply_gender_filter(self=mock_matcher, update=True, )
        mock_matcher.CRUD.apply_gender_filter.assert_not_called()

    @staticmethod
    def test_apply_age_filter(mock_matcher: MagicMock, monkeypatch, ):
        """Tables data are renews every time (fixture)"""
        monkeypatch.setattr(mock_matcher.filters, 'age_range', (20, 50))
        Matcher.apply_age_filter(self=mock_matcher, update=True, )
        mock_matcher.CRUD.apply_age_filter.assert_called_once_with(
            min_age=mock_matcher.filters.age_range[0],
            max_age=mock_matcher.filters.age_range[1],
            connection=mock_matcher.user.connection,
        )
        assert mock_matcher.matches.raw.current == mock_matcher.get_user_matches.return_value

    @staticmethod
    def test_apply_age_filter_any(mock_matcher: MagicMock, monkeypatch, ):
        """Check that filter was not applied and no any changes"""
        monkeypatch.setattr(mock_matcher.filters, 'age_range', tuple(Matcher.Filters.Age))  # Min, Max
        Matcher.apply_age_filter(self=mock_matcher, update=True, )
        mock_matcher.CRUD.apply_age_filter.assert_not_called()

    @staticmethod
    def test_apply_checkboxes_country_filter_true(mock_matcher: MagicMock, monkeypatch, ):
        monkeypatch.setitem(mock_matcher.filters.checkboxes, 'country', True)
        Matcher.apply_checkboxes_country_filter(self=mock_matcher, update=True, )
        mock_matcher.CRUD.apply_checkboxes_country_filter.assert_called_once_with(
            connection=mock_matcher.user.connection,
        )
        assert mock_matcher.matches.raw.current == mock_matcher.get_user_matches.return_value

    @staticmethod
    def test_apply_checkboxes_city_filter_true(mock_matcher: MagicMock, monkeypatch, ):
        monkeypatch.setitem(mock_matcher.filters.checkboxes, 'city', True)
        Matcher.apply_checkboxes_city_filter(self=mock_matcher, update=True, )
        mock_matcher.CRUD.apply_checkboxes_city_filter.assert_called_once_with(
            connection=mock_matcher.user.connection,
        )
        assert mock_matcher.matches.raw.current == mock_matcher.get_user_matches.return_value

    @staticmethod
    def test_apply_checkboxes_photo_filter_true(mock_matcher: MagicMock, monkeypatch, ):
        monkeypatch.setitem(mock_matcher.filters.checkboxes, 'photo', True)
        Matcher.apply_checkboxes_photo_filter(self=mock_matcher, update=True, )
        mock_matcher.CRUD.apply_checkboxes_photo_filter.assert_called_once_with(
            connection=mock_matcher.user.connection,
        )
        assert mock_matcher.matches.raw.current == mock_matcher.get_user_matches.return_value

    @staticmethod
    def test_apply_checkboxes_filter_false(matcher: Matcher, monkeypatch, ):
        for checkbox_name in matcher.filters.checkboxes:
            monkeypatch.setitem(matcher.filters.checkboxes, checkbox_name, False)
            with patch.object(matcher, 'get_user_matches', autospec=True, ) as mock_get_user_covotes:
                matcher.apply_goal_filter(update=True)

            mock_get_user_covotes.assert_not_called()

    @staticmethod
    def test_filter_matches(mock_matcher: MagicMock, ):
        app.models.matches.Matcher.filter_matches(self=mock_matcher, update=True)
        mock_matcher.apply_goal_filter.assert_called_once_with()
        mock_matcher.apply_gender_filter.assert_called_once_with()
        mock_matcher.apply_age_filter.assert_called_once_with()
        mock_matcher.apply_checkboxes_country_filter.assert_called_once_with()
        mock_matcher.apply_checkboxes_city_filter.assert_called_once_with()
        mock_matcher.apply_checkboxes_photo_filter.assert_called_once_with()
        assert mock_matcher.matches.raw.current == mock_matcher.get_user_matches()

    @staticmethod
    def test_set_matches_raw(mock_matcher: MagicMock, ):
        mock_matcher.get_user_matches.return_value = []
        app.models.matches.Matcher.set_matches_raw(self=mock_matcher, )
        mock_matcher.get_user_matches.assert_has_calls([call(new=True), call(new=False), ])
        assert mock_matcher.matches.raw.new == mock_matcher.get_user_matches(new=True)
        assert mock_matcher.matches.raw.all == mock_matcher.get_user_matches(new=False)
        assert mock_matcher.matches.raw.count_new == len(mock_matcher.matches.raw.new)
        assert mock_matcher.matches.raw.count_all == len(mock_matcher.matches.raw.all)

    @staticmethod
    def test_set_matches(mock_matcher: MagicMock, ):
        app.models.matches.Matcher.set_matches(self=mock_matcher, )
        mock_matcher.convert_matches.assert_called_once_with(raw_matches=mock_matcher.matches.raw.all, )
        assert mock_matcher.matches.count_new == len(mock_matcher.matches.new)
        assert mock_matcher.matches.count_all == len(mock_matcher.matches.all)

    @staticmethod
    def test_set_current_matches(matcher: Matcher, ):
        matcher.filters.match_type = matcher.Filters.MatchType.ALL_MATCHES
        matcher.set_current_matches()
        matcher.filters.match_type = matcher.Filters.MatchType.NEW_MATCHES
        matcher.set_current_matches()

    @staticmethod
    def test_convert_matches(mock_matcher: MagicMock, covote: Covote, ):
        mock_matcher.matches.raw.current = [covote]
        result = app.models.matches.Matcher.convert_matches(
            self=mock_matcher,
            raw_matches=mock_matcher.matches.raw.current,
        )
        assert len(mock_matcher.Mapper.Match.mock_calls) == 1
        assert result == [mock_matcher.Mapper.Match.return_value, ]

    class TestMakeSearch:
        """test_make_search"""

        @staticmethod
        def test_make_search_base(mock_matcher: MagicMock, ):
            result = app.models.base.matches.Matcher.make_search(self=mock_matcher, )
            # Checks
            mock_matcher.create_unfiltered_matches.assert_called_once_with(
                drop_old_votes=False, drop_old_matches=False,
            )
            mock_matcher.filter_matches.assert_called_once_with()
            mock_matcher.set_matches_raw.assert_called_once_with()
            assert len(mock_matcher.mock_calls) == 3
            assert result == mock_matcher.matches.raw.all

        @staticmethod
        def test_make_search(mock_matcher: MagicMock, ):
            # Checks
            with patch.object(app.models.base.matches.Matcher, 'make_search', autospec=True, ) as mock_make_search:
                result = app.models.matches.Matcher.make_search(self=mock_matcher, )
                mock_make_search.assert_called_once_with(
                    mock_matcher,
                    drop_old_votes=False,
                    drop_old_matches=False,
                )
                mock_matcher.set_matches.assert_called_once_with()
                assert result == mock_matcher.matches.all

    class TestGetMatch:
        @staticmethod
        def test_pop(mock_matcher: MagicMock, ):
            mock_matcher.matches.current = ['foo', ]
            result = app.models.matches.Matcher.get_match(self=mock_matcher, pop=True, )
            assert result == 'foo'
            assert mock_matcher.matches.current == []

        @staticmethod
        def test_index(mock_matcher: MagicMock, ):
            mock_matcher.matches.current = ['foo', ]
            result = app.models.matches.Matcher.get_match(self=mock_matcher, pop=False, )
            assert result == 'foo'
            assert mock_matcher.matches.current == ['foo', ]

    @staticmethod
    def test_get_common_interests_perc(matcher_s: Matcher, monkeypatch, ):
        monkeypatch.setattr(matcher_s, 'user_votes_count', 20)
        assert matcher_s.get_common_interests_perc(common_posts_count=15) == 75
        monkeypatch.setattr(matcher_s, 'user_votes_count', 27)
        assert matcher_s.get_common_interests_perc(common_posts_count=11) == 41
        monkeypatch.setattr(matcher_s, 'user_votes_count', 14)
        assert matcher_s.get_common_interests_perc(common_posts_count=4) == 29
        monkeypatch.setattr(matcher_s, 'user_votes_count', 16)
        assert matcher_s.get_common_interests_perc(common_posts_count=14) == 88


class TestMatch:

    @staticmethod
    def test_repr(match_s: Match):
        assert match_s.__repr__()

    @staticmethod
    def test_create(mock_match_f: MagicMock):
        app.models.matches.Match.create(self=mock_match_f, )
        mock_match_f.CRUD.create.assert_called_once_with(
            tg_user_id=mock_match_f.owner.tg_user_id,
            matched_tg_user_id=mock_match_f.user.tg_user_id,
            connection=mock_match_f.owner.connection,
        )

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

from app.tg.ptb import keyboards
from app.tg.ptb import constants
from app.tg.ptb.views import View

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    import app.models.matches


class TestWarn:

    @staticmethod
    def test_incorrect_target_goal(mock_tg_view_f: MagicMock, ):
        result = View.Search.Warn.incorrect_target_goal(self=mock_tg_view_f.search.warn, )
        mock_tg_view_f.search.warn.bot.send_message.assert_called_once_with(
            chat_id=mock_tg_view_f.search.warn.tg_user_id,
            text=constants.Search.INCORRECT_TARGET_GOAL,
        )
        assert result == mock_tg_view_f.search.warn.bot.send_message.return_value

    @staticmethod
    def test_incorrect_target_gender(mock_tg_view_f: MagicMock, ):
        result = View.Search.Warn.incorrect_target_gender(self=mock_tg_view_f.search.warn, )
        mock_tg_view_f.search.warn.bot.send_message.assert_called_once_with(
            chat_id=mock_tg_view_f.search.warn.tg_user_id,
            text=constants.Search.INCORRECT_TARGET_GENDER,
        )
        assert result == mock_tg_view_f.search.warn.bot.send_message.return_value

    @staticmethod
    def test_incorrect_target_age(mock_tg_view_f: MagicMock, ):
        result = View.Search.Warn.incorrect_target_age(self=mock_tg_view_f.search.warn, )
        mock_tg_view_f.search.warn.bot.send_message.assert_called_once_with(
            chat_id=mock_tg_view_f.search.warn.tg_user_id,
            text=constants.Search.INCORRECT_TARGET_AGE,
        )
        assert result == mock_tg_view_f.search.warn.bot.send_message.return_value

    @staticmethod
    def test_incorrect_show_option(mock_tg_view_f: MagicMock, ):
        result = View.Search.Warn.incorrect_show_option(self=mock_tg_view_f.search.warn, )
        mock_tg_view_f.search.warn.bot.send_message.assert_called_once_with(
            chat_id=mock_tg_view_f.search.warn.tg_user_id,
            text=constants.Search.INCORRECT_SHOW_OPTION,
        )
        assert result == mock_tg_view_f.search.warn.bot.send_message.return_value

    @staticmethod
    def test_incorrect_show_more_option(mock_tg_view_f: MagicMock, ):
        result = View.Search.Warn.incorrect_show_more_option(self=mock_tg_view_f.search.warn, )
        mock_tg_view_f.search.warn.bot.send_message.assert_called_once_with(
            chat_id=mock_tg_view_f.search.warn.tg_user_id,
            text=constants.Search.INCORRECT_SHOW_MORE_OPTION,
            reply_markup=keyboards.show_one_more_match,
        )
        assert result == mock_tg_view_f.search.warn.bot.send_message.return_value


def test_no_votes(mock_tg_view_f: MagicMock, ):
    result = View.Search.no_votes(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Search.NO_VOTES,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_no_covotes(mock_tg_view_f: MagicMock, ):
    result = View.Search.no_covotes(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Search.NO_COVOTES,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_no_matches_with_filters(mock_tg_view_f: MagicMock, ):
    result = View.Search.no_matches_with_filters(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Search.Result.NO_MATCHES_WITH_FILTERS,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_say_search_hello(mock_tg_view_f: MagicMock, ):
    result = View.Search.say_search_hello(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Search.STEP_0,
        reply_markup=keyboards.go_keyboard
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_ask_target_goal(mock_tg_view_f: MagicMock, ):
    result = View.Search.ask_target_goal(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Search.STEP_1,
        reply_markup=keyboards.ask_target_goal,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_ask_target_gender(mock_tg_view_f: MagicMock, ):
    result = View.Search.ask_target_gender(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Search.STEP_2,
        reply_markup=keyboards.ask_target_gender,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_ask_target_age(mock_tg_view_f: MagicMock, ):
    result = View.Search.ask_target_age(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Search.STEP_3,
        reply_markup=keyboards.ask_target_age,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_show_checkboxes(mock_tg_view_f: MagicMock, mock_ptb_target: MagicMock, ):
    result = View.Search.show_target_checkboxes(self=mock_tg_view_f, target=mock_ptb_target, )
    mock_ptb_target.get_checkboxes_keyboard.assert_called_once_with()
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Search.NEW_FILTERS_SUGGESTIONS,
        reply_markup=mock_ptb_target.get_checkboxes_keyboard.return_value,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_ask_which_matches_show(mock_tg_view_f: MagicMock, mock_matcher: MagicMock, ):
    result = View.Search.ask_which_matches_show(self=mock_tg_view_f, matches=mock_matcher.matches, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Search.Result.FOUND_MATCHES_COUNT.format(FOUND_MATCHES_COUNT=mock_matcher.matches.count_all),
        reply_markup=keyboards.ask_which_matches_show(
            num_all_matches=mock_matcher.matches.count_all,
            num_new_matches=mock_matcher.matches.count_new,
        ),
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_here_match(mock_tg_view_f: MagicMock, match_s: app.models.matches.Match, ):
    result = View.Search.here_match(self=mock_tg_view_f, stats=match_s.stats, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Search.Result.HERE_MATCH.format(
            SHARED_INTERESTS_PERCENTAGE=match_s.stats.common_posts_perc,
            SHARED_INTERESTS_COUNT=match_s.stats.common_posts_count,
        ),
        reply_markup=keyboards.show_one_more_match,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_no_more_matches(mock_tg_view_f: MagicMock, ):
    result = View.Search.no_more_matches(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Search.Result.NO_MORE_MATCHES,
        reply_markup=keyboards.remove(),
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_say_search_goodbye(mock_tg_view_f: MagicMock, ):
    result = View.Search.say_search_goodbye(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=f'{constants.Shared.Words.COMPLETED} {constants.Shared.Words.GOODBYE}',
        reply_markup=keyboards.remove(),
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_update_checkboxes_keyboard(
        mock_tg_view_f: MagicMock,
        mock_ptb_target: MagicMock,
        mock_tg_message: MagicMock,
):
    result = View.Search.update_target_checkboxes_keyboard(message_to_update=mock_tg_message, target=mock_ptb_target, )
    mock_ptb_target.get_checkboxes_keyboard.assert_called_once_with()
    mock_tg_message.edit_reply_markup.assert_called_once_with(
        reply_markup=mock_ptb_target.get_checkboxes_keyboard.return_value,
    )
    assert result == mock_tg_message.edit_reply_markup.return_value


def test_ask_confirm(mock_tg_view_f: MagicMock):
    result = View.Search.ask_confirm(self=mock_tg_view_f)
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=''
             f'{constants.Shared.FOR_READY.format(READY=constants.Shared.Words.READY)}\n'
             f'{constants.Shared.Warn.POSSIBLE_LONG_SEARCH}',
        reply_markup=keyboards.ask_user_confirm,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value

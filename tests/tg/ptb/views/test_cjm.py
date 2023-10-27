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
from unittest.mock import patch
from typing import TYPE_CHECKING

import pytest
# noinspection PyPackageRequirements
from telegram import BotCommand

from app.tg.ptb import keyboards, constants, config
from app.tg.ptb.views import View

if TYPE_CHECKING:
    from unittest.mock import MagicMock


def test_say_statistic_hello(mock_tg_view_f: MagicMock):
    result = View.CJM.say_statistic_hello(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        text=constants.STATISTIC_HELLO,
        chat_id=mock_tg_view_f.tg_user_id,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_show_bot_commands(mock_tg_view_f: MagicMock, ):
    result = View.CJM.show_bot_commands(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=config.PUBLIC_COMMANDS,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_show_bot_commands_remote(mock_tg_view_f: MagicMock, ):
    commands = [BotCommand(command='foo', description='123'), BotCommand(command='bar', description='456'), ]
    mock_tg_view_f.bot.get_my_commands.return_value = commands
    result = View.CJM.show_bot_commands_remote(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=f'{constants.CmdDescriptions.HERE_COMMANDS}/foo - 123\n/bar - 456\n',
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_faq(mock_tg_view_f: MagicMock, ):
    result = View.CJM.faq(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.FAQ,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_show_statistic(mock_tg_view_f: MagicMock, mock_ptb_match_stats: MagicMock, ):
    statistic_text = (
        f'{constants.Search.Profile.TOTAL_LIKES_SET} {mock_ptb_match_stats.opposite_pos_votes_count}: '
        f'{constants.Shared.Words.FROM} {mock_ptb_match_stats.pos_votes_count}.\n'
        f'{constants.Search.Profile.TOTAL_DISLIKES_SET} {mock_ptb_match_stats.opposite_neg_votes_count}: '
        f'{constants.Shared.Words.FROM} {mock_ptb_match_stats.neg_votes_count}.\n'
        f'{constants.Search.Profile.TOTAL_UNMARKED_POSTS} {mock_ptb_match_stats.opposite_zero_votes_count}: '
        f'{constants.Shared.Words.FROM} {mock_ptb_match_stats.zero_votes_count}.\n'
        f'{constants.Search.Profile.SHARED_LIKES_PERCENTAGE}: {mock_ptb_match_stats.common_pos_votes_perc}%\n'
        f'{constants.Search.Profile.SHARED_DISLIKES_PERCENTAGE}: {mock_ptb_match_stats.common_neg_votes_perc}%\n'
        f'{constants.Search.Profile.SHARED_UNMARKED_POSTS_PERCENTAGE}: '
        f'{mock_ptb_match_stats.common_zero_votes_perc}%\n'
    )
    with patch.object(keyboards, 'remove', autospec=True, ) as mock_remove:
        result = View.CJM.show_statistic(self=mock_tg_view_f, match_stats=mock_ptb_match_stats, )
    mock_ptb_match_stats.user.get_tg_name.assert_called_once_with(entity=mock_ptb_match_stats.with_tg_user_id, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=(
            f'{constants.HERE_STATISTICS_WITH} '
            f'{mock_ptb_match_stats.user.get_tg_name.return_value} '
            f'(id {mock_ptb_match_stats.with_tg_user_id}):'
        ),
    )
    mock_remove.assert_called_once_with()
    mock_tg_view_f.bot.send_photo.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        photo=mock_ptb_match_stats.get_pie_chart_result(),  # TODO rename
        caption=statistic_text,
        reply_markup=mock_remove.return_value,
    )
    assert result == (mock_tg_view_f.bot.send_message.return_value, mock_tg_view_f.bot.send_photo.return_value,)


def test_start_scenario(mock_tg_view_f: MagicMock, ):
    result = View.CJM.start_scenario(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.START_SCENARIO.format(
            config.PERSONAL_SCENARIO_COMMAND,
            config.GLOBAL_SCENARIO_COMMAND,
        ),
        reply_markup=keyboards.start_scenario,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_global_scenario_show_collections(mock_tg_view_f: MagicMock, ):
    """Show collections to sender"""
    result = View.CJM.global_scenario_show_collections(self=mock_tg_view_f.cjm, collections=['foo'], )
    mock_tg_view_f.cjm.collections_view.show_collections.assert_called_once_with(
        text=f'{constants.GLOBAL_SCENARIO}\n{constants.Shared.FOR_READY.format(READY=config.SEARCH_COMMAND)}',
        collections=['foo'],
    )
    assert result == mock_tg_view_f.cjm.collections_view.show_collections.return_value


def test_global_scenario_notify_ready_keyword(mock_tg_view_f: MagicMock, ):
    """Show collections to sender"""
    result = View.CJM.global_scenario_notify_ready_keyword(self=mock_tg_view_f.cjm, )
    mock_tg_view_f.cjm.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.cjm.tg_user_id,
        text=constants.Shared.FOR_READY.format(READY=config.SEARCH_COMMAND, ),
        reply_markup=keyboards.search_cmd_btn,
    )
    assert result == mock_tg_view_f.cjm.bot.send_message.return_value


@pytest.mark.parametrize(
    argnames=('collections', 'text'),
    argvalues=(  # Different text for different collection len
            (['foo'], constants.PERSONAL_SCENARIO),
            (['foo'] * 10, f'{constants.PERSONAL_SCENARIO}\n{constants.Shared.FOR_READY}'),
    ), )
def test_personal_scenario(mock_tg_view_f: MagicMock, text: str, collections: list[str], ):
    result = View.CJM.personal_scenario_show_collections(self=mock_tg_view_f.cjm, collections=collections, )
    mock_tg_view_f.cjm.collections_view.show_collections.assert_called_once_with(
        text=text,
        collections=collections,
    )
    assert result == mock_tg_view_f.cjm.collections_view.show_collections.return_value

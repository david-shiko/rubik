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

from app.tg.ptb import keyboards, constants
from app.tg.ptb.config import PUBLIC_COMMANDS
from app.tg.ptb.views.base import log, Base, Shared

if TYPE_CHECKING:
    # noinspection PyPackageRequirements
    from telegram.ext import ExtBot

from app.tg.ptb.config import SEARCH_COMMAND

if TYPE_CHECKING:
    # noinspection PyPackageRequirements
    from telegram import (
        Bot,
        Message,
    )
    from app.tg.ptb.classes.matches import MatchStatsInterface  # Ok, cuz no such tg ptb module
    from app.tg.ptb.classes.users import User
    from app.tg.ptb.views.collections import Collections as CollectionsView
    from app.tg.ptb.classes import collections as ptb_collections

"""
Customer Journey Map (scenarios / usecases)
"""


class CJM(Base, ):

    def __init__(self, user: User, bot: Bot | ExtBot, collections_view: CollectionsView, shared_view: Shared, ):
        super().__init__(user=user, bot=bot, )
        self.collections_view = collections_view
        self.shared_view = shared_view

    @log
    def show_bot_commands(self, ) -> Message:
        """Repeat TG bot description from a local obj"""
        return self.bot.send_message(chat_id=self.tg_user_id, text=PUBLIC_COMMANDS, )

    @log
    def show_bot_commands_remote(self, ) -> Message:
        """Repeat TG bot description from the sever"""
        commands = ''.join([f"/{command.command} - {command.description}\n" for command in self.bot.get_my_commands()])
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=f'{constants.CmdDescriptions.HERE_COMMANDS}{commands}',
        )

    @log
    def faq(self, ) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.FAQ,
        )

    @log
    def say_statistic_hello(self, ) -> Message:
        return self.bot.send_message(chat_id=self.tg_user_id, text=constants.STATISTIC_HELLO, )

    @log
    def show_statistic(
            self,
            match_stats: MatchStatsInterface,
            tg_user_id: int | None = None,
    ) -> tuple[Message, Message]:
        tg_user_id = tg_user_id or self.tg_user_id
        with_tg_name = match_stats.user.get_tg_name(entity=match_stats.with_tg_user_id, )
        message_1 = self.bot.send_message(
            chat_id=tg_user_id,
            text=f'{constants.HERE_STATISTICS_WITH} {with_tg_name} (id {match_stats.with_tg_user_id}):',
        )
        statistic_text = (
            f'{constants.Search.Profile.TOTAL_LIKES_SET} {match_stats.opposite_pos_votes_count}: '
            f'{constants.Shared.Words.FROM} {match_stats.pos_votes_count}.\n'
            f'{constants.Search.Profile.TOTAL_DISLIKES_SET} {match_stats.opposite_neg_votes_count}: '
            f'{constants.Shared.Words.FROM} {match_stats.neg_votes_count}.\n'
            f'{constants.Search.Profile.TOTAL_UNMARKED_POSTS} {match_stats.opposite_zero_votes_count}: '
            f'{constants.Shared.Words.FROM} {match_stats.zero_votes_count}.\n'
            f'{constants.Search.Profile.SHARED_LIKES_PERCENTAGE}: {match_stats.common_pos_votes_perc}%\n'
            f'{constants.Search.Profile.SHARED_DISLIKES_PERCENTAGE}: {match_stats.common_neg_votes_perc}%\n'
            f'{constants.Search.Profile.SHARED_UNMARKED_POSTS_PERCENTAGE}: {match_stats.common_zero_votes_perc}%\n'
        )
        message_2 = self.bot.send_photo(
            chat_id=tg_user_id,
            photo=match_stats.get_pie_chart_result(),
            caption=statistic_text,
            reply_markup=keyboards.remove(),
        )
        return message_1, message_2

    @log
    def start_scenario(self, ) -> Message:
        sent_message = self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.START_SCENARIO,
            reply_markup=keyboards.start_scenario,
        )
        return sent_message

    @log
    def global_scenario_show_collections(self, collections: list[ptb_collections.Collection], ) -> Message:
        """Show collections to sender"""
        return self.collections_view.show_collections(
            text=f'{constants.GLOBAL_SCENARIO}\n{constants.Shared.FOR_READY.format(READY=SEARCH_COMMAND)}',
            collections=collections,
        )

    @log
    def global_scenario_notify_ready_keyword(self, ) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.Shared.FOR_READY.format(READY=SEARCH_COMMAND, ),
            reply_markup=keyboards.search_cmd_btn,
        )

    @log
    def personal_scenario_show_collections(self, collections: list[ptb_collections.Collection], ) -> Message:
        """Show collections to sender"""
        text = constants.PERSONAL_SCENARIO
        if len(collections) > 8:  # If many posts user may miss for ready notification. 8 is just approximate number.
            text = f'{constants.PERSONAL_SCENARIO}\n{constants.Shared.FOR_READY}'
        return self.collections_view.show_collections(text=text, collections=collections, )

    @log
    def remove_sharing_button(self, message: Message, ) -> bool:  # Rename to remove_sharing_message ?
        return self.shared_view.remove_proposal_message(message_id_to_delete=message.message_id, )

    class Deprecated:  # pragma: no cover
        """Not in use"""

        def __init__(self, user: User, bot: Bot | ExtBot, ):
            # Bot is indeed the same for all instances, but can't be a class attribute because not exists yet
            self.bot = bot
            self.tg_user_id = user.tg_user_id
            self.tg_name = user.tg_name

        @log
        def no_more_posts(self, ) -> Message:
            return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Deprecated.NO_MORE_POSTS, )

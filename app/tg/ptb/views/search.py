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
from app.tg.ptb.views.base import log, Base
from app.tg.ptb.classes import matches as ptb_matches

if TYPE_CHECKING:
    # noinspection PyPackageRequirements
    from telegram import Bot, Message, MessageId
    # noinspection PyPackageRequirements
    from telegram.ext import ExtBot
    from app.tg.ptb.forms.user import Target  # Put model into target and use it
    from app.tg.ptb.classes.users import User


class Search(Base, ):

    class Warn(Base, ):
        @log
        def incorrect_target_goal(self, ) -> Message:
            return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Search.INCORRECT_TARGET_GOAL, )

        @log
        def incorrect_target_gender(self, ) -> Message:
            return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Search.INCORRECT_TARGET_GENDER, )

        @log
        def incorrect_target_age(self, ) -> Message:
            return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Search.INCORRECT_TARGET_AGE, )

        @log
        def incorrect_show_option(self, ) -> Message:
            return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Search.INCORRECT_SHOW_OPTION, )

        @log
        def incorrect_show_more_option(self, ) -> Message:
            return self.bot.send_message(
                chat_id=self.tg_user_id,
                text=constants.Search.INCORRECT_SHOW_MORE_OPTION,
                reply_markup=keyboards.show_one_more_match,
            )

    def __init__(self, bot: Bot | ExtBot, user: User, ):
        super().__init__(user=user, bot=bot, )
        self.warn = self.Warn(user=user, bot=bot, )

    @log
    def say_search_hello(self, ) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.Search.STEP_0,
            reply_markup=keyboards.go_keyboard,
        )

    @log
    def no_votes(self, ) -> Message:
        return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Search.NO_VOTES, )

    @log
    def no_covotes(self, ) -> Message:
        return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Search.NO_COVOTES, )

    @log
    def ask_target_goal(self, ) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.Search.STEP_1,
            reply_markup=keyboards.ask_target_goal,
        )

    @log
    def ask_target_gender(self, ) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.Search.STEP_2,
            reply_markup=keyboards.ask_target_gender
        )

    @log
    def ask_target_age(self, ) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.Search.STEP_3,
            reply_markup=keyboards.ask_target_age
        )

    @log
    def show_target_checkboxes(self, target: Target, ) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.Search.NEW_FILTERS_SUGGESTIONS,
            reply_markup=target.get_checkboxes_keyboard(),
        )

    @log
    def ask_confirm(self, ready_keyword: str = constants.Shared.Words.READY, ) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=(
                f'{constants.Shared.FOR_READY.format(READY=ready_keyword)}\n'
                f'{constants.Shared.Warn.POSSIBLE_LONG_SEARCH}'
            ),
            reply_markup=keyboards.ask_user_confirm,
        )

    @log
    def no_matches_with_filters(self, ) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.Search.Result.NO_MATCHES_WITH_FILTERS,
        )

    @log
    def ask_which_matches_show(self, matches: ptb_matches.Matcher.Matches, ) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.Search.Result.FOUND_MATCHES_COUNT.format(FOUND_MATCHES_COUNT=matches.count_all, ),
            reply_markup=keyboards.ask_which_matches_show(
                num_all_matches=matches.count_all,
                num_new_matches=matches.count_new,
            ), )

    @log
    def here_match(self, stats: ptb_matches.Match.Stats, ) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.Search.Result.HERE_MATCH.format(
                SHARED_INTERESTS_PERCENTAGE=stats.common_posts_perc,
                SHARED_INTERESTS_COUNT=stats.common_posts_count,
            ),
            reply_markup=keyboards.show_one_more_match,
        )

    @staticmethod
    def update_target_checkboxes_keyboard(message_to_update: Message, target: Target, ) -> Message | bool:
        return message_to_update.edit_reply_markup(reply_markup=target.get_checkboxes_keyboard(), )

    @log
    def no_more_matches(self, ) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.Search.Result.NO_MORE_MATCHES,
            reply_markup=keyboards.remove(),
        )

    @log
    def say_search_goodbye(self, ) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=f'{constants.Shared.Words.COMPLETED} {constants.Shared.Words.GOODBYE}',
            reply_markup=keyboards.remove(),
        )

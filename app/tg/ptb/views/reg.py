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
from app.tg.ptb.classes import users as ptb_users

if TYPE_CHECKING:
    # noinspection PyPackageRequirements
    from telegram import Bot, Message, ReplyKeyboardMarkup as tg_RKM
    # noinspection PyPackageRequirements
    from telegram.ext import ExtBot
    from app.tg.ptb.classes.users import User
    from app.tg.ptb.classes.users import ProfileInterface


class Reg(Base, ):
    class Warn(Base, ):
        SharedView = Shared

        @log
        def incorrect_name(self, ) -> Message:
            return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Reg.INCORRECT_NAME, )

        @log
        def incorrect_goal(self, ) -> Message:
            return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Reg.INCORRECT_GOAL, )

        @log
        def incorrect_gender(self, ) -> Message:
            return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Reg.INCORRECT_GENDER, )

        @log
        def incorrect_age(self, ) -> Message:
            return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Reg.INCORRECT_AGE, )

        @log
        def incorrect_location(self, ) -> Message:
            return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Reg.INCORRECT_LOCATION, )

        @log
        def no_profile_photos(self, ) -> Message:
            return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Reg.NO_PROFILE_PHOTOS, )

        @log
        def too_many_photos(self, keyboard: tg_RKM, used_photos: int, ):
            return self.bot.send_message(
                chat_id=self.tg_user_id,
                text=constants.Reg.TOO_MANY_PHOTOS.format(
                    USED_PHOTOS=used_photos,
                    MAX_PHOTOS=ptb_users.User.MAX_PHOTOS_COUNT,
                ),
                reply_markup=keyboard,
            )

        @log
        def incorrect_photo(self, keyboard: tg_RKM, ):
            return self.bot.send_message(
                chat_id=self.tg_user_id,
                text=constants.Shared.Warn.INCORRECT_FINISH,
                reply_markup=keyboard,
            )

        @log
        def comment_too_long(self, comment_len: int, ):
            return self.SharedView.Warn.text_too_long(
                max_symbols=ptb_users.User.MAX_COMMENT_LEN,
                used_symbols=comment_len,
            )

        @log
        def incorrect_end_reg(self, ) -> Message:
            return self.bot.send_message(chat_id=self.tg_user_id, text=constants.Reg.END_REG_HELP, )

    def __init__(self, bot: Bot | ExtBot, user: User, ):
        super().__init__(user=user, bot=bot, )
        self.warn = self.Warn(user=user, bot=bot, )

    def say_reg_hello(self, ) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.Reg.STEP_0,
            reply_markup=keyboards.go_keyboard,
        )

    @log
    def ask_user_name(self, ) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.Reg.STEP_1,
            reply_markup=keyboards.ask_user_name(self.tg_name),
        )

    @log
    def ask_user_goal(self, ) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.Reg.STEP_2,
            reply_markup=keyboards.ask_user_goal,
        )

    @log
    def ask_user_gender(self, ) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.Reg.STEP_3,
            reply_markup=keyboards.ask_user_gender,
        )

    @log
    def ask_user_age(self, ) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.Reg.STEP_4,
            reply_markup=keyboards.ask_user_age,
        )

    @log
    def ask_user_location(self, ) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.Reg.STEP_5,
            reply_markup=keyboards.ask_user_location,
        )

    @log
    def ask_user_photos(self, ) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.Reg.STEP_6,
            reply_markup=keyboards.original_photo_keyboard,
        )

    @log
    def say_photo_added_success(self, keyboard: tg_RKM) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.Reg.PHOTOS_ADDED_SUCCESS,
            reply_markup=keyboard,
        )

    @log
    def say_photos_removed_success(self, keyboard: tg_RKM, ) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.Reg.PHOTOS_REMOVED_SUCCESS,
            reply_markup=keyboard,
        )

    @log
    def ask_user_comment(self, ) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.Reg.STEP_7,
            reply_markup=keyboards.skip_cancel, )

    @log
    def say_success_reg(self, ) -> Message:
        return self.bot.send_message(
            chat_id=self.tg_user_id,
            text=f'{constants.Reg.SUCCESS_REG}\n{constants.MORE_ACTIONS}\n{PUBLIC_COMMANDS}',
            reply_markup=keyboards.remove(),
        )

    @log
    def show_profile(self, profile: ProfileInterface, ) -> None:
        self.bot.send_message(
            chat_id=self.tg_user_id,
            text=constants.Reg.HERE_PROFILE_PREVIEW,
            reply_markup=keyboards.ask_user_confirm,
        )
        profile.send(show_to_tg_user_id=self.tg_user_id, )

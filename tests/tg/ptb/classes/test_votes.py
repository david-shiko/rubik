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


import app.tg.ptb.classes.posts

if TYPE_CHECKING:
    from app.models.users import User
    from app.tg.ptb.classes.votes import PublicVote, PersonalVote
    from app.tg.ptb.classes.posts import PublicPost, PersonalPost
    # noinspection PyPackageRequirements
    from telegram import CallbackQuery as tg_CallbackQuery
    # noinspection PyPackageRequirements
    from telegram import InlineKeyboardMarkup as tg_IKM


class TestVote:

    class TestCallbackToVote:
        @staticmethod
        def body(
                vote: PublicVote | PersonalVote,
                user: User,
                callback_query: tg_CallbackQuery,
                keyboard: tg_IKM,
        ):
            for keyboard_row in keyboard.inline_keyboard:
                for button in keyboard_row:
                    callback_query.data = str(button.callback_data)
                    assert vote.callback_to_vote(user=user, callback=callback_query, )

        def test_public(
                self,
                user_s: User,
                ptb_public_post_s: PublicPost,
                ptb_public_vote_s: PublicVote,
                tg_callback_query_f: tg_CallbackQuery,
        ):
            keyboard = app.tg.ptb.classes.posts.PublicPost.get_keyboard_deprecated(self=ptb_public_post_s, )
            self.body(keyboard=keyboard, user=user_s, vote=ptb_public_vote_s, callback_query=tg_callback_query_f, )

        def test_personal(
                self,
                user_s: User,
                ptb_personal_post_s: PersonalPost,
                ptb_personal_vote_s: PersonalVote,
                tg_callback_query_f: tg_CallbackQuery,
        ):
            keyboard = app.tg.ptb.classes.posts.PersonalPost.get_keyboard(
                self=ptb_personal_post_s,
                clicker_vote=ptb_personal_vote_s,
                opposite_vote=ptb_personal_vote_s,
            )
            self.body(keyboard=keyboard, user=user_s, vote=ptb_personal_vote_s, callback_query=tg_callback_query_f, )

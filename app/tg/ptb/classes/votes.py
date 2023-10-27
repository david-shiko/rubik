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
from abc import ABC
from typing import Type, TYPE_CHECKING

import app.tg.classes.votes

if TYPE_CHECKING:
    # noinspection PyPackageRequirements
    from telegram import CallbackQuery
    import app.tg.ptb.classes.users


class VoteBase:
    @classmethod
    def callback_to_vote(
            cls: Type[PublicVote | PersonalVote],
            user: app.tg.ptb.classes.users.User,
            callback: CallbackQuery,
    ) -> PublicVote | PersonalVote:
        """Convert str callback to vote object"""
        post_id = vote_value = int(callback.data.split()[-1])
        # noinspection PyArgumentList
        return cls(
            user=user,
            post_id=abs(post_id),
            message_id=callback.message.message_id,
            value=cls.convert_vote_value(raw_value=vote_value),
        )


class PublicVoteInterface(app.tg.classes.votes.PublicVoteInterface, ABC, ):
    ...


class PublicVote(app.tg.classes.votes.PublicVote, VoteBase, PublicVoteInterface, ):
    ...


class PersonalVoteInterface(app.tg.classes.votes.PersonalVoteInterface, ABC, ):
    ...


class PersonalVote(app.tg.classes.votes.PersonalVote, VoteBase, PersonalVoteInterface, ):
    ...

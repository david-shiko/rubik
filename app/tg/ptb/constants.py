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

from app.config import BOT_NAME

from app import constants

from app.tg.ptb.config import (
    CREATE_PERSONAL_POST_COMMAND,
    GET_PUBLIC_POST_COMMAND,
    REG_COMMAND,
    GLOBAL_SCENARIO_COMMAND,
    PERSONAL_SCENARIO_COMMAND,
    SEARCH_COMMAND,
)
from app.tg.ptb.classes.collections import Collection
from app.tg.ptb.classes.users import User
from app.tg.classes.posts import PostsChannels

"""Exactly the same constants as in app constants but with filled ptb layer values"""

MORE_ACTIONS = constants.MORE_ACTIONS

TMP_RESTRICTION = constants.TMP_RESTRICTION

USER_GOT_SHARE_PROPOSAL = constants.USER_GOT_SHARE_PROPOSAL  # format(USER_ID, )
USER_GOT_REQUEST_PROPOSAL = constants.USER_GOT_REQUEST_PROPOSAL  # format(USER_ID, )
USER_DECLINED_REQUEST_PROPOSAL = constants.USER_DECLINED_REQUEST_PROPOSAL
USER_DECLINED_SHARE_PROPOSAL = constants.USER_DECLINED_SHARE_PROPOSAL

REG_REQUIRED = constants.REG_REQUIRED.format(REG_CMD=REG_COMMAND, )
POSSIBLE_INACTIVE_ACCOUNT = constants.POSSIBLE_INACTIVE_ACCOUNT
ENTER_THE_NUMBER = constants.ENTER_THE_NUMBER

ERROR_VOTE = constants.ERROR_VOTE

STATISTIC_HELLO = constants.STATISTIC_HELLO
HERE_STATISTICS_WITH = constants.HERE_STATISTICS_WITH

FAQ = constants.FAQ.format(
    BOT_NAME=BOT_NAME,
    REG_CMD=REG_COMMAND,
    GLOBAL_SCENARIO_CMD=GLOBAL_SCENARIO_COMMAND,
    PERSONAL_SCENARIO_CMD=PERSONAL_SCENARIO_COMMAND,
    SEARCH_CMD=SEARCH_COMMAND,
)
START_SCENARIO = constants.START_SCENARIO.format(
    GLOBAL_SCENARIO_CMD=GLOBAL_SCENARIO_COMMAND,
    PERSONAL_SCENARIO_CMD=PERSONAL_SCENARIO_COMMAND,
)
GLOBAL_SCENARIO = constants.GLOBAL_SCENARIO.format(
    POSTS_CHANNEL_LINK=PostsChannels.POSTS_LINK.value,
    MAX_POSTS_COUNT=Collection.MAX_POSTS_COUNT,
)
PERSONAL_SCENARIO = constants.PERSONAL_SCENARIO.format(
    MAX_POSTS_COUNT=Collection.MAX_POSTS_COUNT,
)

I_AM_BOT = constants.I_AM_BOT
EASTER_EGG = constants.EASTER_EGG

INTERNAL_ERROR = constants.INTERNAL_ERROR


class Collections(constants.Collections):
    MAX_NAME_LEN = constants.Collections.MAX_NAME_LEN.format(MAX_NAME_LEN=Collection.MAX_NAME_LEN, )
    NO_COLLECTIONS = constants.Collections.NO_COLLECTIONS.format(
        CREATE_PERSONAL_POST_CMD=CREATE_PERSONAL_POST_COMMAND,
    )


class Reg(constants.Reg):
    TOO_MANY_PHOTOS = constants.Reg.TOO_MANY_PHOTOS.format(MAX_PHOTOS=User.MAX_PHOTOS_COUNT, )  # format(USED_PHOTOS, )
    COMMAND_FOR_REG = constants.Reg.COMMAND_FOR_REG.format(REG_CMD=REG_COMMAND, )


class Shared(constants.Shared, ):
    ...


class Search(constants.Search, ):
    NO_VOTES = constants.Search.NO_VOTES.format(
        POSTS_CHANNEL_LINK=PostsChannels.POSTS_LINK.value,
        GLOBAL_SCENARIO_CMD=GLOBAL_SCENARIO_COMMAND,
        GET_PUBLIC_POST_CMD=GET_PUBLIC_POST_COMMAND,
    )
    NO_COVOTES = constants.Search.NO_COVOTES.format(
        POSTS_CHANNEL_LINK=PostsChannels.POSTS_LINK.value,
        GLOBAL_SCENARIO_CMD=GLOBAL_SCENARIO_COMMAND,
        GET_PUBLIC_POST_CMD=GET_PUBLIC_POST_COMMAND,
    )


class Posts(constants.Posts, ):
    constants.Posts.Personal.NO_POSTS = constants.Posts.Personal.NO_POSTS.format(
        CREATE_PERSONAL_POST_CMD=CREATE_PERSONAL_POST_COMMAND,
    )


class CmdDescriptions(constants.CmdDescriptions, ):
    ...


class Deprecated(constants.Deprecated, ):
    REG_REQUIRED_FOR_VOTING = constants.Deprecated.REG_REQUIRED_FOR_VOTING.format(
        REG_CMD=REG_COMMAND,
    )


class FutureFeature(constants.FutureFeature, ):
    ...


class Regexp(constants.Regexp, ):
    ...

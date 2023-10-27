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
from re import compile, IGNORECASE

from app.config import MAIN_ADMIN_NAME
from app.utils import StringFormatDefault  # Allow to use default arg for str.format
from app.postconfig import translators

"""
Some format values are accessible on this stage but python don't allow to fill only few of format placeholders.
For this case there a workaround - double brackets ( {{ PLACEHOLDER }} ).
See: https://stackoverflow.com/a/18343661/11277611
"""

MORE_ACTIONS = translators.messages("MORE_ACTIONS")

TMP_RESTRICTION = translators.messages("TMP_RESTRICTION")

# The same for posts and collections
USER_GOT_SHARE_PROPOSAL = translators.messages("USER_GOT_SHARE_PROPOSAL")  # format(USER_ID, USERNAME)
USER_GOT_REQUEST_PROPOSAL = translators.messages("USER_GOT_REQUEST_PROPOSAL")  # format(USER_ID, USERNAME )
USER_DECLINED_REQUEST_PROPOSAL = translators.messages("USER_DECLINED_REQUEST_PROPOSAL")  # format(USER_ID, )
# Common for many
USER_DECLINED_SHARE_PROPOSAL = translators.messages("USER_DECLINED_SHARE_PROPOSAL")  # format(USER_ID, )

REG_REQUIRED = translators.messages("REG_REQUIRED")  # format(REG_CMD, )
POSSIBLE_INACTIVE_ACCOUNT = translators.messages("POSSIBLE_INACTIVE_ACCOUNT")
ENTER_THE_NUMBER = translators.messages("ENTER_THE_NUMBER")

ERROR_VOTE = translators.messages("ERROR_VOTE")

STATISTIC_HELLO = translators.messages("STATISTIC_HELLO")
HERE_STATISTICS_WITH = translators.messages("HERE_STATISTICS_WITH")

# format(REG_CMD, GLOBAL_SCENARIO_CMD, PERSONAL_SCENARIO_CMD, SEARCH_CMD, )
FAQ = str(translators.messages("FAQ")).format(MAIN_ADMIN_NAME=MAIN_ADMIN_NAME, )
START_SCENARIO = translators.messages("START_SCENARIO")
GLOBAL_SCENARIO = translators.messages("GLOBAL_SCENARIO").format(READY=translators.messages("READY"))  # format(MAX_POSTS_COUNT, )
PERSONAL_SCENARIO = translators.messages("PERSONAL_SCENARIO").format(READY=translators.messages("READY"))  # MAX_POSTS_COUNT

I_AM_BOT = translators.messages("I_AM_BOT")
EASTER_EGG = translators.messages("EASTER_EGG_KEYBOARD")

INTERNAL_ERROR = translators.messages("INTERNAL_ERROR")


class Shared:
    class Profile:
        """Titles of the fields, aka keys"""
        NAME = translators.messages("NAME")
        GOAL = translators.messages("GOAL")
        GENDER = translators.messages("GENDER")
        AGE = translators.messages("AGE")
        LOCATION = translators.messages("LOCATION")
        ABOUT = translators.messages("ABOUT")

    class Words:
        """Single words cls"""
        FROM = translators.messages("FROM")
        UNKNOWN = translators.messages("UNKNOWN")
        OK = translators.messages("OK")
        GO = translators.messages("GO")
        HELP = translators.messages("HELP")
        SEND = translators.messages("SEND")
        FORWARD = translators.messages("FORWARD")
        CONTINUE = translators.messages("CONTINUE")
        READY = FINISH = translators.messages("READY")
        COMPLETE = translators.messages("COMPLETE")
        COMPLETED = translators.messages("COMPLETED")
        CANCELED = translators.messages("CANCELED")
        GOODBYE = translators.messages("GOODBYE")
        SKIP = translators.messages("SKIP")
        BACK = translators.messages("BACK")
        CANCEL = translators.messages("CANCEL")
        PENDING = translators.messages("PENDING")
        # Kinda buttons
        ALLOW = translators.messages("ALLOW")
        DISALLOW = translators.messages("DISALLOW")
        ACCEPT = translators.messages("ACCEPT")
        WAIT = translators.messages("WAIT")
        DECLINE = translators.messages("DECLINE")

    class Warn:
        UNSKIPPABLE_STEP = translators.messages("UNSKIPPABLE_STEP")
        UNCLICKABLE_BUTTON = translators.messages("UNCLICKABLE_BUTTON")
        MISUNDERSTAND = translators.messages("MISUNDERSTAND")
        ALAS_USER_NOT_FOUND = translators.messages("ALAS_USER_NOT_FOUND")
        POSSIBLE_LONG_SEARCH = translators.messages("POSSIBLE_LONG_SEARCH")
        TEXT_TOO_LONG = translators.messages("TEXT_TOO_LONG")  # format(MAX_TEXT_LEN, USED_TEXT_LEN, )
        ERROR_EXPLANATION = translators.messages("COMMON_ERROR_EXPLANATION")
        ERROR_LOCATION_SERVICE = translators.messages("ERROR_LOCATION_SERVICE")
        NICKNAME_SEARCH_NOT_IMPLEMENTED = translators.messages("NICKNAME_SEARCH_NOT_IMPLEMENTED")
        INCORRECT_FINISH = translators.messages("INCORRECT_FINISH")  # format(Words.FINISH, )
        INCORRECT_SEND = translators.messages("INCORRECT_SEND")
        INCORRECT_CONTINUE = translators.messages("INCORRECT_CONTINUE")
        INCORRECT_USER = translators.messages("INCORRECT_USER")

    Warn.INCORRECT_CONTINUE = StringFormatDefault(
        string=Warn.INCORRECT_CONTINUE,
        defaults=dict(MISUNDERSTAND=Warn.MISUNDERSTAND, CONTINUE=Words.CONTINUE, CANCEL=Words.CANCEL, ),
    )
    Warn.INCORRECT_FINISH = Warn.INCORRECT_FINISH.format(MISUNDERSTAND=Warn.MISUNDERSTAND, READY=Words.READY)
    FOR_READY = ASK_CONFIRM = StringFormatDefault(
        string=translators.messages("FOR_READY"),
        defaults={'READY': Words.READY},
    )


class Reg:
    class Buttons:
        REMOVE_PHOTOS = translators.reg("REMOVE_PHOTOS")
        USE_ACCOUNT_NAME = translators.reg("USE_ACCOUNT_NAME")
        USE_ACCOUNT_PHOTOS = translators.reg("USE_ACCOUNT_PHOTOS")
        SEND_LOCATION = translators.reg("SEND_LOCATION")
        I_MALE = translators.reg("I_MALE")
        I_FEMALE = translators.reg("I_FEMALE")
        I_WANNA_CHAT = translators.reg("I_WANNA_CHAT")
        I_WANNA_DATE = translators.reg("I_WANNA_DATE")
        I_WANNA_CHAT_AND_DATE = translators.reg("I_WANNA_CHAT_AND_DATE")

    class Profile:
        I_MALE: Reg.Buttons.I_MALE
        I_FEMALE: Reg.Buttons.I_FEMALE
        I_WANNA_CHAT: Reg.Buttons.I_WANNA_CHAT
        I_WANNA_DATE: Reg.Buttons.I_WANNA_DATE
        I_WANNA_CHAT_AND_DATE: Reg.Buttons.I_WANNA_CHAT_AND_DATE

    Profile.I_MALE = Buttons.I_MALE
    Profile.I_FEMALE = Buttons.I_FEMALE
    Profile.I_WANNA_CHAT = Buttons.I_WANNA_CHAT
    Profile.I_WANNA_DATE = Buttons.I_WANNA_DATE
    Profile.I_WANNA_CHAT_AND_DATE = Buttons.I_WANNA_CHAT_AND_DATE

    REG_GOALS = TARGET_GOALS = [
        Buttons.I_WANNA_CHAT,
        Buttons.I_WANNA_DATE,
        Buttons.I_WANNA_CHAT_AND_DATE,
    ]
    REG_GENDERS = [Buttons.I_MALE, Buttons.I_FEMALE, ]

    COMMAND_FOR_REG = translators.reg("COMMAND_FOR_REG")  # format(REG_CMD=REG_COMMAND, )

    STEP_0 = translators.reg("REG_STEP_0")
    STEP_1 = translators.reg("REG_STEP_1")
    STEP_2 = translators.reg("REG_STEP_2")
    STEP_3 = translators.reg("REG_STEP_3")
    STEP_4 = translators.reg("REG_STEP_4")
    STEP_5 = translators.reg("REG_STEP_5")
    STEP_6 = translators.reg("REG_STEP_6")
    STEP_7 = translators.reg("REG_STEP_7")

    HERE_PROFILE_PREVIEW = translators.reg("HERE_PROFILE_PREVIEW")
    SUCCESS_REG = translators.reg("SUCCESS_REG")

    _YOU_CAN_ADD_MORE_PHOTOS = translators.reg("_YOU_CAN_ADD_MORE_PHOTOS")
    PHOTOS_ADDED_SUCCESS = translators.reg("PHOTOS_ADDED_SUCCESS")
    PHOTOS_REMOVED_SUCCESS = translators.reg("PHOTOS_REMOVED_SUCCESS")
    PHOTO_ADDED_SUCCESS = translators.reg("PHOTO_ADDED_SUCCESS")
    NO_PHOTOS_TO_REMOVE = translators.reg("NO_PHOTOS_TO_REMOVE")
    TOO_MANY_PHOTOS = translators.reg("TOO_MANY_PHOTOS")  # format(USED_PHOTOS, MAX_PHOTOS_COUNT, )
    NO_PROFILE_PHOTOS = translators.reg("NO_PROFILE_PHOTOS")

    INCORRECT_NAME = Shared.Warn.MISUNDERSTAND
    INCORRECT_GOAL = translators.reg("INCORRECT_GOAL").format(
        MISUNDERSTAND=Shared.Warn.MISUNDERSTAND,
        I_WANNA_CHAT=Buttons.I_WANNA_CHAT,
        I_WANNA_DATE=Buttons.I_WANNA_DATE,
        I_WANNA_CHAT_AND_DATE=Buttons.I_WANNA_CHAT_AND_DATE,
    )
    INCORRECT_GENDER = translators.reg("INCORRECT_GENDER").format(
        MISUNDERSTAND=Shared.Warn.MISUNDERSTAND,
        I_MALE=Buttons.I_MALE,
        I_FEMALE=Buttons.I_FEMALE,
    )  # No specific
    INCORRECT_AGE = translators.reg("INCORRECT_AGE").format(MISUNDERSTAND=Shared.Warn.MISUNDERSTAND, )
    INCORRECT_LOCATION = translators.reg("INCORRECT_LOCATION").format(MISUNDERSTAND=Shared.Warn.MISUNDERSTAND, )

    ERROR_LOCATION_SERVICE = Shared.Warn.ERROR_LOCATION_SERVICE
    ERROR_SAVING_PHOTOS = translators.reg("ERROR_SAVING_PHOTOS")
    ERROR_SAVING_PROFILE = translators.reg("ERROR_SAVING_PROFILE")

    END_REG_HELP = translators.reg("END_REG_HELP").format(
        MISUNDERSTAND=Shared.Warn.MISUNDERSTAND,
        FINISH=Shared.Words.FINISH,
        BACK=Shared.Words.BACK,
        CANCEL=Shared.Words.CANCEL,
    )


class Search:
    class Checkboxes:
        AGE_SPECIFIED = translators.search("AGE_SPECIFIED")
        COUNTRY_SPECIFIED = translators.search("COUNTRY_SPECIFIED")
        CITY_SPECIFIED = translators.search("CITY_SPECIFIED")
        PHOTO_SPECIFIED = translators.search("PHOTO_SPECIFIED")

    class Buttons:
        MALE = translators.search('MALE')
        FEMALE = translators.search('FEMALE')
        ANY_GENDER = translators.search("ANY_GENDER")
        I_WANNA_CHAT = translators.search("I_WANNA_CHAT")  # reg translator is ok
        I_WANNA_DATE = translators.search("I_WANNA_DATE")  # reg translator is ok
        I_WANNA_CHAT_AND_DATE = translators.search("I_WANNA_CHAT_AND_DATE")  # reg translator is ok
        ANY_AGE = translators.search("ANY_AGE")
        SHOW_ALL = translators.search("SHOW_ALL")
        SHOW_NEW = translators.search("SHOW_NEW")
        SHOW_MORE = translators.search("SHOW_MORE")
        FINISH = Shared.Words.FINISH

    class Result:
        NO_MATCHES_WITH_FILTERS = translators.search("NO_MATCHES_WITH_FILTERS")
        FOUND_MATCHES_COUNT = translators.search("FOUND_MATCHES_COUNT")  # format(FOUND_MATCHES_COUNT, )
        HERE_MATCH = translators.search("HERE_MATCH")  # format(SHARED_INTERESTS_PERCENTAGE, SHARED_INTERESTS_COUNT, )
        NO_MORE_MATCHES = translators.search("NO_MORE_MATCHES")

    class Profile:
        TOTAL_LIKES_SET = translators.search("TOTAL_LIKES_SET")
        TOTAL_DISLIKES_SET = translators.search("TOTAL_DISLIKES_SET")
        TOTAL_UNMARKED_POSTS = translators.search("TOTAL_UNMARKED_POSTS")
        SHARED_LIKES_PERCENTAGE = translators.search("SHARED_LIKES_PERCENTAGE")
        SHARED_DISLIKES_PERCENTAGE = translators.search("SHARED_DISLIKES_PERCENTAGE")
        SHARED_UNMARKED_POSTS_PERCENTAGE = translators.search("SHARED_UNMARKED_POSTS_PERCENTAGE")
        IT_WANNA_CHAT = translators.search("IT_WANNA_CHAT")
        IT_WANNA_DATE = translators.search("IT_WANNA_DATE")
        CHAT_AND_DATE = translators.search("IT_WANNA_CHAT_AND_DATE")
        MALE: str
        FEMALE: str

    Profile.MALE = Buttons.MALE
    Profile.FEMALE = Buttons.FEMALE

    NO_VOTES = translators.search("NO_VOTES")
    NO_COVOTES = translators.search("NO_COVOTES")

    STEP_0 = translators.search("SEARCH_STEP_0")
    STEP_1 = translators.search("SEARCH_STEP_1")
    STEP_2 = translators.search("SEARCH_STEP_2")
    STEP_3 = translators.search("SEARCH_STEP_3")
    STEP_4 = Shared.FOR_READY

    NEW_FILTERS_SUGGESTIONS = translators.search("NEW_FILTERS_SUGGESTIONS").format(ADMIN=MAIN_ADMIN_NAME, )
    ERROR_FILTERS = translators.search("ERROR_FILTERS")
    TARGET_GOALS = [
        Buttons.I_WANNA_CHAT,
        Buttons.I_WANNA_DATE,
        Buttons.I_WANNA_CHAT_AND_DATE,
    ]
    TARGET_GENDERS = [translators.search('MALE'), translators.search('FEMALE'), translators.search('ANY_GENDER'), ]
    TARGET_SHOW_CHOICE = [translators.search('SHOW_ALL'), translators.search('SHOW_NEW'), ]

    INCORRECT_TARGET_GOAL = translators.search("INCORRECT_TARGET_GOAL").format(
        MISUNDERSTAND=Shared.Warn.MISUNDERSTAND,
        I_WANNA_CHAT=Buttons.I_WANNA_CHAT,
        I_WANNA_DATE=Buttons.I_WANNA_DATE,
        I_WANNA_CHAT_AND_DATE=Buttons.I_WANNA_CHAT_AND_DATE,
    )
    INCORRECT_TARGET_GENDER = translators.search("INCORRECT_TARGET_GENDER").format(
        MISUNDERSTAND=Shared.Warn.MISUNDERSTAND,
        MALE=Buttons.MALE,
        FEMALE=Buttons.FEMALE,
        ANY_GENDER=Buttons.ANY_GENDER,
    )
    INCORRECT_TARGET_AGE = translators.search("INCORRECT_TARGET_AGE").format(
        MISUNDERSTAND=Shared.Warn.MISUNDERSTAND,
        ANY_AGE=Buttons.ANY_AGE,
    )
    INCORRECT_SHOW_OPTION = translators.search("INCORRECT_SHOW_OPTION").format(
        MISUNDERSTAND=Shared.Warn.MISUNDERSTAND,
        SHOW_ALL=Buttons.SHOW_ALL,
        SHOW_NEW=Buttons.SHOW_NEW,
    )
    INCORRECT_SHOW_MORE_OPTION = translators.search("INCORRECT_SHOW_MORE_OPTION").format(
        MISUNDERSTAND=Shared.Warn.MISUNDERSTAND,
        SHOW_MORE=Buttons.SHOW_MORE,
        FINISH=Buttons.FINISH,
    )


class Collections:
    ASK_FOR_NAMES = translators.collections("ASK_FOR_NAMES")
    MAX_NAME_LEN = translators.collections("MAX_NAME_LEN")  # format(MAX_NAME_LEN)
    ASK_TO_SHARE = translators.collections("ASK_TO_SHARE")
    COLLECTIONS_TO_SHARE_NOT_CHOSE = translators.collections("COLLECTIONS_TO_SHARE_NOT_CHOSE")
    NO_POSTS = translators.collections("NO_POSTS")
    NO_COLLECTIONS = translators.collections("NO_COLLECTIONS")  # format(CREATE_PERSONAL_POST_CMD)

    NOTIFY_SHARE_PROPOSAL = translators.collections("NOTIFY_SHARE_PROPOSAL")  # format(USER_ID)
    WHO_TO_SHARE = translators.collections("WHO_TO_SHARE")
    HERE_YOUR_COLLECTIONS = translators.collections("HERE_YOUR")
    HERE_SHARED = translators.collections("HERE_SHARED")

    SAY_CHOSE_FOR_POST = translators.collections("SAY_CHOSE_FOR_POST")
    HERE_POSTS = translators.collections("HERE_POSTS")

    SHARED_COLLECTIONS_NOT_FOUND = translators.collections("SHARED_COLLECTIONS_NOT_FOUND")
    USER_DECLINED_SHARE_PROPOSAL = translators.messages("USER_DECLINED_SHARE_PROPOSAL")  # format(USER_ID, )
    USER_ACCEPTED_SHARE_PROPOSAL = translators.collections("USER_ACCEPTED_SHARE_PROPOSAL")  # format(USER_ID)


class Posts:
    class Public:
        class Buttons:
            PENDING = Shared.Words.PENDING
            READY_TO_RELEASE = translators.posts("READY_TO_RELEASE")

        NO_PENDING = translators.posts("NO_PENDING")
        HELLO = translators.posts("PUBLIC_POST_HELLO")
        NO_NEW_POSTS = translators.posts("NO_NEW_POSTS")
        NO_MASS_POSTS = translators.posts("NO_MASS_POSTS")

    HERE_POST_PREVIEW = translators.posts("HERE_POST_PREVIEW")
    POST_TO_VOTE_NOT_FOUND = translators.posts("POST_TO_VOTE_NOT_FOUND")
    NOT_FOUND = translators.posts("POST_NOT_FOUND")
    ERROR_CREATE = translators.posts("ERROR_CREATE")
    CREATED_SUCCESSFULLY = translators.posts("POST_CREATED_SUCCESSFULLY")

    class Personal:
        class Buttons:
            ALLOW = Shared.Words.ALLOW
            DISALLOW = Shared.Words.DISALLOW
            ACCEPT = Shared.Words.ACCEPT
            DECLINE = Shared.Words.DECLINE

        WHO_TO_SHARE = translators.posts("WHO_TO_SHARE")
        WHO_TO_REQUEST = translators.posts("WHO_TO_REQUEST")
        NOTIFY_SHARE_PROPOSAL = translators.posts("NOTIFY_SHARE_PROPOSAL")  # format(USER_ID)
        NOTIFY_REQUEST_PROPOSAL = translators.posts("NOTIFY_REQUEST_PROPOSAL")  # format(USER_ID)
        USER_DECLINED_SHARE_PROPOSAL = translators.posts("USER_DECLINED_SHARE_PROPOSAL")  # format(USER_ID, )
        USER_ACCEPTED_SHARE_PROPOSAL = translators.posts("USER_ACCEPTED_SHARE_PROPOSAL")  # format(USER_ID)
        # USER_DECLINES_SHARE_PROPOSAL = USER_DECLINED_INVITE  # format(USER_ID)
        USER_ACCEPTED_REQUEST_PROPOSAL = translators.posts("USER_ACCEPTED_REQUEST_PROPOSAL")  # format(USER_ID)
        USER_DECLINED_REQUEST_PROPOSAL = USER_DECLINED_REQUEST_PROPOSAL  # format(USER_ID)
        SENDER_HAS_NO_POSTS = translators.posts("SENDER_HAS_NO_PERSONAL_POSTS")

        HELLO = translators.posts("PERSONAL_POST_HELLO")
        NO_POSTS = translators.posts("NO_PERSONAL_POSTS")  # format(CREATE_PERSONAL_POST_CMD)
        HERE_YOUR_POSTS = translators.posts("HERE_YOUR_PERSONAL_POSTS")
        CANT_SEND_TO_THIS_USER = translators.posts("CANT_SEND_POSTS_TO_THIS_USER")


class CmdDescriptions:
    HERE_COMMANDS = translators.cmd_descriptions("HERE_COMMANDS")
    FAQ = translators.cmd_descriptions("FAQ")
    BOT_USER_COMMANDS = translators.cmd_descriptions("BOT_USER_COMMANDS")
    GLOBAL_SEARCH = translators.cmd_descriptions("GLOBAL_SEARCH")
    START = translators.cmd_descriptions("START")
    SEARCH = translators.cmd_descriptions("SEARCH")
    REG = translators.cmd_descriptions("REG")
    PUBLIC_POST = translators.cmd_descriptions("PUBLIC_POST")
    PERSONAL_POST = translators.cmd_descriptions("PERSONAL_POST")
    SHARE_PERSONAL_POSTS = translators.cmd_descriptions("SHARE_PERSONAL_POSTS")
    REQUEST_PERSONAL_POSTS = translators.cmd_descriptions("REQUEST_PERSONAL_POSTS")
    GET_NEW_PUBLIC_POST = translators.cmd_descriptions("GET_NEW_PUBLIC_POST")
    GET_PERSONAL_POSTS = translators.cmd_descriptions("GET_PERSONAL_POSTS")
    GET_COLLECTIONS = translators.cmd_descriptions("GET_COLLECTIONS")
    GET_STAT = translators.cmd_descriptions("GET_STAT")
    GLOBAL_SCENARIO = translators.cmd_descriptions("GLOBAL_SCENARIO")
    PERSONAL_SCENARIO = translators.cmd_descriptions("PERSONAL_SCENARIO")
    SHOW_SAMPLE = translators.cmd_descriptions("SHOW_SAMPLE")


class Deprecated:
    # format(TMP_RESTRICTION, REG_CMD, )
    REG_REQUIRED_FOR_VOTING = translators.messages("REG_REQUIRED_FOR_VOTING").format(TMP_RESTRICTION=TMP_RESTRICTION, )
    NO_MORE_POSTS = translators.posts("NO_MORE_POSTS")


class FutureFeature:
    ASK_POST_ID = translators.messages("ASK_POST_ID")


class Regexp:
    CANCEL_R = compile(f'^{Shared.Words.CANCEL}$', IGNORECASE)
    BACK_R = compile(f'^{Shared.Words.BACK}$', IGNORECASE)
    SKIP_R = compile(f'^{Shared.Words.SKIP}$', IGNORECASE)

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

import logging
from dataclasses import dataclass
from re import compile, IGNORECASE
from time import sleep as time_sleep
from typing import TYPE_CHECKING, Callable
# noinspection PyPackageRequirements
from telegram.bot import Bot

import app.postconfig
from app.config import DEBUG, LOG_VIEW_FILEPATH

if TYPE_CHECKING:
    import app.db.manager
    import app.models.users


def create_view_logger() -> logging.Logger:
    class CustomFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord):  # LogRecord similar to str
            if isinstance(record.msg, str):
                record.msg = record.msg.strip().replace('\n', '')
                return super(CustomFormatter, self).format(record)

    handler = logging.FileHandler(filename=LOG_VIEW_FILEPATH, )
    # ".80s" - limit log record to N symbols
    handler.setFormatter(fmt=CustomFormatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    handler.setLevel(level=logging.INFO, )
    view_logger = logging.getLogger(name='view_logger', )
    view_logger.propagate = False  # Don't send events to parents loggers (default behavior)
    view_logger.setLevel(level=logging.INFO, )
    view_logger.addHandler(hdlr=handler, )
    return view_logger


@dataclass
class Config:
    bot: Bot
    # noinspection PyUnresolvedReferences
    logger: logging.Logger = app.postconfig.logger
    view_logger: logging.Logger = create_view_logger()
    sleep_function: Callable = time_sleep
    is_log: bool = DEBUG


PUBLIC_VOTE_CBK_S = 'public_vote'
CHANNEL_PUBLIC_VOTE_CBK_S = 'channel_public_vote'
PERSONAL_VOTE_CBK_S = 'personal_vote'
CHECKBOX_CBK_S = 'checkboxes'
ACCEPT_PERSONAL_POSTS_CBK_S = 'accept_personal_posts'
ACCEPT_COLLECTIONS_CBK_S = 'accept_collections'
REQUEST_PERSONAL_POSTS_CBK_S = 'request_personal_posts'
UPDATE_PUBLIC_POST_STATUS_CBK_S = 'update_public_post_status'
SHOW_COLLECTION_CBK_S = 'show_collection'
# Especially for personal scenario posts sharing cuz posts cbk handler for global and personal scenario are different
SHOW_COLLECTION_POSTS_CBK_S = 'show_collection_posts'
MARK_COLLECTION_CBK_S = 'mark_collection'
MARK_SHOW_COLLECTION_CBK_S = 'mark_show_collection'
EMPTY_CBK_S = 'foo'

GET_PUBLIC_POST_S = 'get_public_post'
GET_PENDING_POSTS_S = 'get_pending_posts'
GET_MY_PERSONAL_POSTS_S = 'get_my_personal_posts'
GET_MY_COLLECTIONS_S = 'get_my_collections'
GET_DEFAULT_COLLECTIONS_S = 'get_default_collections'  # Not in use
GET_MY_PERSONAL_POSTS_COLLECTIONS_S = 'get_my_personal_posts_collections'
GEN_BOTS_S = 'gen_bots'
GEN_ME_S = 'gen_me'
ALL_BOT_COMMANDS_S = 'all_commands'
FAQ_S = 'faq'

REG_S = 'reg'
SEND_S = 'send'
POST_S = 'post'
GET_BOT_ALL_COMMANDS_S = 'all_commands'
SEARCH_S = 'search'
START_S = 'start'
CREATE_PUBLIC_POST_S = 'create_public_post'
CREATE_PERSONAL_POST_S = 'create_personal_post'
CREATE_COLLECTION_S = 'create_collection'
SHARE_PERSONAL_POSTS_S = 'share_personal_posts'
REQUEST_PERSONAL_POSTS_S = 'request_personal_posts'
SHARE_COLLECTIONS_S = 'share_collections'
GET_STATISTIC_WITH_S = 'get_stats_with'
PERSONAL_SCENARIO_S = 'personal_scenario'
GLOBAL_SCENARIO_S = 'global_scenario'
PERSONAL_EXAMPLE_S = 'personal_example'

# COMMANDS

FAQ_COMMAND = f'/{FAQ_S}'
ALL_BOT_COMMANDS_COMMAND = f'/{ALL_BOT_COMMANDS_S}'
GET_PUBLIC_POST_COMMAND = f'/{GET_PUBLIC_POST_S}'
GET_PENDING_POSTS_COMMAND = f'/{GET_PENDING_POSTS_S}'
GET_DEFAULT_COLLECTIONS_COMMAND = f'/{GET_DEFAULT_COLLECTIONS_S}'  # Not in use
GET_MY_COLLECTIONS_COMMAND = f'/{GET_MY_COLLECTIONS_S}'
GET_MY_PERSONAL_POSTS_COMMAND = f'/{GET_MY_PERSONAL_POSTS_S}'
SEND_COMMAND = f'/{SEND_S}'
POST_COMMAND = f'/{POST_S}'
REG_COMMAND = f'/{REG_S}'
SEARCH_COMMAND = f'/{SEARCH_S}'
START_COMMAND = f'/{START_S}'
CREATE_PUBLIC_POST_COMMAND = f'/{CREATE_PUBLIC_POST_S}'
CREATE_PERSONAL_POST_COMMAND = f'/{CREATE_PERSONAL_POST_S}'
SHARE_PERSONAL_POSTS_COMMAND = f'/{SHARE_PERSONAL_POSTS_S}'
REQUEST_PERSONAL_POSTS_COMMAND = f'/{REQUEST_PERSONAL_POSTS_S}'
CREATE_COLLECTION_COMMAND = f'/{CREATE_COLLECTION_S}'
SHARE_COLLECTIONS_COMMAND = f'/{SHARE_COLLECTIONS_S}'
GET_STATISTIC_WITH_COMMAND = f'/{GET_STATISTIC_WITH_S}'
GEN_BOTS_COMMAND = f'/{GEN_BOTS_S}'
GEN_ME_COMMAND = f'/{GEN_ME_S}'
GET_BOT_ALL_COMMANDS_COMMAND = f'/{GET_BOT_ALL_COMMANDS_S}'
PERSONAL_SCENARIO_COMMAND = f'/{PERSONAL_SCENARIO_S}'
GLOBAL_SCENARIO_COMMAND = f'/{GLOBAL_SCENARIO_S}'
PERSONAL_EXAMPLE_COMMAND = f'/{PERSONAL_EXAMPLE_S}'

PUBLIC_COMMANDS = (
    f'{FAQ_COMMAND} - {app.constants.CmdDescriptions.FAQ}\n'
    f'{GET_BOT_ALL_COMMANDS_COMMAND} - {app.constants.CmdDescriptions.BOT_USER_COMMANDS}\n'
    f'{SEARCH_COMMAND} - {app.constants.CmdDescriptions.SEARCH}\n'
    f'{START_COMMAND} - {app.constants.CmdDescriptions.START}\n'
    f'{REG_COMMAND} - {app.constants.CmdDescriptions.REG}\n'
    f'{CREATE_PUBLIC_POST_COMMAND} - {app.constants.CmdDescriptions.PUBLIC_POST}\n'
    f'{CREATE_PERSONAL_POST_COMMAND} - {app.constants.CmdDescriptions.PERSONAL_POST}\n'
    f'{SHARE_PERSONAL_POSTS_COMMAND} - {app.constants.CmdDescriptions.SHARE_PERSONAL_POSTS}\n'
    f'{REQUEST_PERSONAL_POSTS_COMMAND} - {app.constants.CmdDescriptions.REQUEST_PERSONAL_POSTS}\n'
    f'{GET_PUBLIC_POST_COMMAND} - {app.constants.CmdDescriptions.GET_NEW_PUBLIC_POST}\n'
    f'{GET_MY_PERSONAL_POSTS_COMMAND} - {app.constants.CmdDescriptions.GET_PERSONAL_POSTS}\n'
    f'{GET_MY_COLLECTIONS_COMMAND} - {app.constants.CmdDescriptions.GET_COLLECTIONS}\n'
    f'{GET_STATISTIC_WITH_COMMAND} - {app.constants.CmdDescriptions.GET_STAT}\n'
    f'{GLOBAL_SCENARIO_COMMAND} - {app.constants.CmdDescriptions.GLOBAL_SCENARIO}\n'
    f'{PERSONAL_SCENARIO_COMMAND} - {app.constants.CmdDescriptions.PERSONAL_SCENARIO}\n'
    f'{PERSONAL_EXAMPLE_COMMAND} - {app.constants.CmdDescriptions.SHOW_SAMPLE}\n'
)

REG_R = compile(REG_COMMAND, IGNORECASE)  # ^ - start of string, $ - end of string
START_SEARCH_R = compile(SEARCH_S, IGNORECASE)
CREATE_PUBLIC_POST_R = compile(CREATE_PUBLIC_POST_COMMAND, IGNORECASE)
CREATE_PERSONAL_POST_R = compile(CREATE_PERSONAL_POST_COMMAND, IGNORECASE)
SHARE_PERSONAL_POSTS_R = compile(SHARE_PERSONAL_POSTS_COMMAND, IGNORECASE)
REQUEST_PERSONAL_POSTS_R = compile(REQUEST_PERSONAL_POSTS_COMMAND, IGNORECASE)
GET_STATISTIC_WITH_R = compile(GET_STATISTIC_WITH_COMMAND, IGNORECASE)

# ^ - exactly starts with
# $ - exactly ends with
# \d+ - number (note: just \d is digit, not a number)
PUBLIC_VOTE_CBK_R = compile(r'^public_vote', )
CHANNEL_PUBLIC_VOTE_CBK_R = compile(r'^channel_public_vote', )
PERSONAL_VOTE_CBK_R = compile(r'^personal_vote', )
CHECKBOX_CBK_R = compile(r'^checkboxes', )
ACCEPT_PERSONAL_POSTS_CBK_R = compile(r'^accept_personal_posts', )
ACCEPT_COLLECTIONS_CBK_R = compile(r'^accept_collections', )
REQUEST_PERSONAL_POSTS_CBK_R = compile(r'^request_personal_posts', )
UPDATE_PUBLIC_POST_STATUS_CBK_R = compile(r'^update_public_post_status', )
SHOW_COLLECTION_CBK_R = compile(r'^show_collection \d+$', )  # text that ending with digits
# Especially for personal scenario posts sharing cuz posts cbk handler for global and personal scenario are different
SHOW_COLLECTION_POSTS_CBK_R = compile(r'^show_collection_posts \d+ \d+$', )
MARK_COLLECTION_CBK_R = compile(r'^mark_collection \d$')  # \d - digit
MARK_SHOW_COLLECTION_CBK_R = compile(r'^mark_show_collection \d+$', )  # text that ending with digits
EMPTY_CBK_R = compile(r'^foo', )

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
from typing import Callable, Any, TYPE_CHECKING, Iterable, TypedDict, Optional

# noinspection PyPackageRequirements
from telegram import (
    ReplyKeyboardMarkup as tg_RKM,
    KeyboardButton as tg_KB,
    ReplyKeyboardRemove as tg_ReplyKeyboardRemove,
)

import app.tg.ptb.config

if TYPE_CHECKING:
    import app.structures.base

"""Logically it's a part of tg/ptb.views """


def cancel_factory(buttons: Iterable[tg_KB | str], *args, **kwargs, ) -> tg_RKM:
    """May be improved by making keyboard (default cancel) as param"""
    [kwargs.pop(key, None) for key in ('keyboard', 'resize_keyboard', 'one_time_keyboard')]
    return tg_RKM(
        keyboard=[
            buttons,  # Row above
            [app.constants.Shared.Words.CANCEL],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
        *args,
        **kwargs,
    )


def ask_which_matches_show(num_all_matches: int = 0, num_new_matches: int = 0, ):
    return tg_RKM(
        keyboard=[
            [f'{app.constants.Search.Buttons.SHOW_ALL} ({num_all_matches})'],
            [f'{app.constants.Search.Buttons.SHOW_NEW} ({num_new_matches})'],
            [app.constants.Shared.Words.CANCEL, ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


reg = tg_RKM(
    keyboard=[[app.tg.ptb.config.REG_COMMAND]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

continue_cancel = tg_RKM(
    keyboard=[[app.constants.Shared.Words.CONTINUE], [app.constants.Shared.Words.CANCEL]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

ready_cancel = tg_RKM(
    keyboard=[[app.constants.Shared.Words.READY], [app.constants.Shared.Words.CANCEL]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

send_cancel = tg_RKM(
    keyboard=[[app.constants.Shared.Words.SEND], [app.constants.Shared.Words.CANCEL]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

original_photo_keyboard = tg_RKM(
    keyboard=[
        [app.constants.Shared.Words.FINISH],
        [app.constants.Reg.Buttons.USE_ACCOUNT_PHOTOS],
        [app.constants.Shared.Words.CANCEL],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

add_any_photo = tg_RKM(
    keyboard=[
        [app.constants.Shared.Words.FINISH],
        [app.constants.Reg.Buttons.USE_ACCOUNT_PHOTOS],
        [app.constants.Reg.Buttons.REMOVE_PHOTOS],
        [app.constants.Shared.Words.CANCEL],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

remove_photos = tg_RKM(
    keyboard=[
        [app.constants.Shared.Words.FINISH],
        [app.constants.Reg.Buttons.REMOVE_PHOTOS],
        [app.constants.Shared.Words.CANCEL]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

go_keyboard = tg_RKM(
    keyboard=[[app.constants.Shared.Words.GO], [app.constants.Shared.Words.CANCEL]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

ask_user_name: Callable[[Any], tg_RKM] = lambda name: tg_RKM(
    keyboard=[[f'{app.constants.Reg.Buttons.USE_ACCOUNT_NAME} ("{name}")'], [app.constants.Shared.Words.CANCEL]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

ask_user_goal = tg_RKM(
    keyboard=[
        [app.constants.Reg.Buttons.I_WANNA_CHAT, app.constants.Reg.Buttons.I_WANNA_DATE],
        [app.constants.Reg.Buttons.I_WANNA_CHAT_AND_DATE],
        [app.constants.Shared.Words.CANCEL],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

ask_user_gender = tg_RKM(
    keyboard=[
        [app.constants.Reg.Buttons.I_FEMALE, app.constants.Reg.Buttons.I_MALE],
        [app.constants.Shared.Words.CANCEL]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

cancel = ask_user_age = tg_RKM(
    keyboard=[[app.constants.Shared.Words.CANCEL]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

skip_cancel = tg_RKM(
    keyboard=[[app.constants.Shared.Words.SKIP], [app.constants.Shared.Words.CANCEL]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

finish_cancel = tg_RKM(
    keyboard=[[app.constants.Shared.Words.FINISH], [app.constants.Shared.Words.CANCEL]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

ask_user_location = tg_RKM(
    keyboard=[
        [tg_KB(text=app.constants.Reg.Buttons.SEND_LOCATION, request_location=True)],
        [app.constants.Shared.Words.SKIP],
        [app.constants.Shared.Words.CANCEL],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

apply_filters = ask_user_confirm = tg_RKM(
    keyboard=[
        [app.constants.Shared.Words.FINISH],
        [app.constants.Shared.Words.CANCEL],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

search_cmd_btn = tg_RKM(
    [[app.tg.ptb.config.SEARCH_COMMAND]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

ask_target_goal = ask_user_goal

ask_target_gender = tg_RKM(
    keyboard=[
        [app.constants.Search.Buttons.MALE, app.constants.Search.Buttons.FEMALE],
        [app.constants.Search.Buttons.ANY_GENDER],
        [app.constants.Shared.Words.CANCEL],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

ask_target_age = tg_RKM(
    keyboard=[
        [app.constants.Search.Buttons.ANY_AGE], [app.constants.Shared.Words.CANCEL]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

show_one_more_match = tg_RKM(
    keyboard=[[app.constants.Search.Buttons.SHOW_MORE], [app.constants.Shared.Words.COMPLETE]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

create_personal_post = tg_RKM(
    keyboard=[[app.tg.ptb.config.CREATE_PERSONAL_POST_COMMAND]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

remove = tg_ReplyKeyboardRemove

start_scenario = tg_RKM(
    keyboard=[[app.tg.ptb.config.PERSONAL_SCENARIO_COMMAND], [app.tg.ptb.config.GLOBAL_SCENARIO_COMMAND]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

global_scenario = tg_RKM(
    keyboard=[[app.tg.ptb.config.PERSONAL_SCENARIO_COMMAND], [app.tg.ptb.config.GLOBAL_SCENARIO_COMMAND]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

global_scenario_notify_search_keyword = tg_RKM(
    keyboard=[[app.tg.ptb.config.SEARCH_COMMAND], [app.constants.Shared.Words.CANCEL]],
    resize_keyboard=True,
    one_time_keyboard=True,
)

personal_scenario = tg_RKM(
    keyboard=[
        [app.tg.ptb.config.GET_MY_COLLECTIONS_COMMAND],
        [app.constants.Shared.Words.SKIP],
        [app.constants.Shared.Words.CANCEL]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

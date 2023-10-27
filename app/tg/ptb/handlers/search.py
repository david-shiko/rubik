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

# noinspection PyPackageRequirements
from telegram import Update

import app.constants
import app.exceptions

import app.tg.ptb.utils
import app.tg.ptb.forms.user

if TYPE_CHECKING:
    from custom_ptb.callback_context import CustomCallbackContext as CallbackContext

COMPLETE_KEYWORD = app.constants.Shared.Words.COMPLETE


def entry_point(_, context):
    context.user_data.view.search.say_search_hello()
    return 0


def entry_point_handler(update: Update, context: CallbackContext):
    try:
        context.user_data.forms.target = app.tg.ptb.forms.user.Target(user=context.user_data.current_user, )
        context.user_data.forms.target.handle_start_search(text=update.effective_message.text, )
    except app.exceptions.NoVotes:  # Use directly context.user_data.current_user.matcher.is_user_has_votes?
        context.user_data.view.search.no_votes()
        return app.tg.ptb.utils.end_conversation()
    except app.exceptions.NoCovotes:  # Use directly context.user_data.current_user.matcher.is_user_has_covotes?
        context.user_data.view.search.no_covotes()
        return app.tg.ptb.utils.end_conversation()
    context.user_data.view.search.ask_target_goal()
    return 1


def goal_handler(update: Update, context: CallbackContext):
    try:
        context.user_data.forms.target.handle_goal(text=update.effective_message.text, )
    except app.exceptions.IncorrectProfileValue:
        context.user_data.view.search.warn.incorrect_target_goal()
        return
    context.user_data.view.search.ask_target_gender()
    return 2


def gender_handler(update: Update, context: CallbackContext):
    try:
        context.user_data.forms.target.handle_gender(text=update.effective_message.text, )
    except app.exceptions.IncorrectProfileValue:
        context.user_data.view.search.warn.incorrect_target_gender()
        return
    context.user_data.view.search.ask_target_age()
    return 3


def age_handler(update: Update, context: CallbackContext):
    try:
        context.user_data.forms.target.handle_age(text=update.effective_message.text, )
    except app.exceptions.IncorrectProfileValue:
        context.user_data.view.search.warn.incorrect_target_age()
        return
    context.user_data.view.search.show_target_checkboxes(target=context.user_data.forms.target, )
    context.user_data.view.search.ask_confirm()  # Send message to make delay. The answer is no matter.
    return 4


def checkboxes_handler(_: Update, context: CallbackContext):
    context.user_data.current_user.matcher.make_search()
    if context.user_data.current_user.matcher.matches.all:  # If user has matches
        context.user_data.view.search.ask_which_matches_show(matches=context.user_data.current_user.matcher.matches, )
    else:
        context.user_data.view.search.no_matches_with_filters()
        return app.tg.ptb.utils.end_conversation()
    return 5


def match_type_handler(update: Update, context: CallbackContext):
    try:
        context.user_data.forms.target.handle_show_option(text=update.effective_message.text, )
    except app.exceptions.IncorrectProfileValue:
        context.user_data.view.search.warn.incorrect_show_option()
        return
    if match := context.user_data.current_user.matcher.get_match():  # Show first match to wait user input
        context.user_data.view.search.here_match(stats=match.stats, )
        match.show()
    else:
        context.user_data.view.search.no_more_matches()
        return app.tg.ptb.utils.end_conversation()
    return 6


def show_match_handler(update: Update, context: CallbackContext):
    message_text = update.effective_message.text.lower().strip()
    if message_text == app.constants.Search.Buttons.SHOW_MORE.lower():
        if match := context.user_data.current_user.matcher.get_match():
            context.user_data.view.search.here_match(stats=match.stats, )
            match.show()  # use view?
            return
        else:
            context.user_data.view.search.no_more_matches()
            return app.tg.ptb.utils.end_conversation()
    elif message_text == COMPLETE_KEYWORD.lower():
        context.user_data.view.search.say_search_goodbye()
        return app.tg.ptb.utils.end_conversation()
    else:
        context.user_data.view.search.warn.incorrect_show_more_option()
        return


def checkbox_cbk_handler(update: Update, context: CallbackContext) -> None:
    _, button_name = update.callback_query.data.split()
    context.user_data.forms.target.filters.checkboxes[button_name] ^= 1  # Swap between 1 and 0
    context.user_data.view.search.update_target_checkboxes_keyboard(
        message_to_update=update.effective_message,
        target=context.user_data.forms.target,
    )
    update.callback_query.answer()
    return

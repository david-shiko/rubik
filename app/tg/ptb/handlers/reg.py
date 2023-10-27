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
# noinspection PyPackageRequirements
from telegram.ext.conversationhandler import ConversationHandler

import app.constants
import app.exceptions
import app.tg.ptb.utils
import app.tg.ptb.forms.user

if TYPE_CHECKING:
    from custom_ptb.callback_context import CustomCallbackContext as CallbackContext

FINISH_KEYWORD = app.constants.Shared.Words.FINISH
INCORRECT_FINISH_KEYWORD = app.constants.Shared.Warn.INCORRECT_FINISH


def entry_point(_: Update, context: CallbackContext, ):
    context.user_data.view.reg.say_reg_hello()
    return 0


def entry_point_handler(_: Update, context: CallbackContext, ):
    context.user_data.forms.new_user = app.tg.ptb.forms.user.NewUser(user=context.user_data.current_user, )
    context.user_data.view.reg.ask_user_name()
    return 1


def name_handler(update: Update, context: CallbackContext, ):
    try:
        context.user_data.forms.new_user.handle_name(text=update.effective_message.text, )
    except app.exceptions.IncorrectProfileValue:
        context.user_data.view.reg.warn.incorrect_name()
        return
    context.user_data.view.reg.ask_user_goal()
    return 2


def goal_handler(update: Update, context: CallbackContext, ):
    try:
        context.user_data.forms.new_user.handle_goal(text=update.effective_message.text, )
    except app.exceptions.IncorrectProfileValue:
        context.user_data.view.reg.warn.incorrect_goal()
        return
    context.user_data.view.reg.ask_user_gender()
    return 3


def gender_handler(update: Update, context: CallbackContext, ):
    try:
        context.user_data.forms.new_user.handle_gender(text=update.effective_message.text, )
    except app.exceptions.IncorrectProfileValue:
        context.user_data.view.reg.warn.incorrect_gender()
        return
    context.user_data.view.reg.ask_user_age()
    return 4


def age_handler(update: Update, context: CallbackContext, ):
    try:
        context.user_data.forms.new_user.handle_age(text=update.effective_message.text, )
    except app.exceptions.IncorrectProfileValue:
        context.user_data.view.reg.warn.incorrect_age()
        return
    context.user_data.view.reg.ask_user_location()
    return 5


def location_handler_geo(update: Update, context: CallbackContext, ):  # user_city don't have validation
    """
    Maybe no necessary to get the country from the location, as the country may be determined incorrectly ?
    Perhaps no need to get city from the location, as the user may want to specify only a country ?
    """
    try:
        context.user_data.forms.new_user.handle_location_geo(location=update.effective_message.location, )
    except app.exceptions.BadLocation:
        context.user_data.view.reg.warn.incorrect_location()
        return
    except app.exceptions.LocationServiceError:
        context.user_data.view.location_service_error()
        return
    context.user_data.view.reg.ask_user_photos()
    return 6


def location_handler_text(update: Update, context: CallbackContext, ):  # user_city don't have validation
    """
    Maybe no necessary to get the country from the location, as the country may be determined incorrectly ?
    Perhaps no need to get city from the location, as the user may want to specify only a country ?
    """
    try:
        context.user_data.forms.new_user.handle_location_text(text=update.effective_message.text, )
    except app.exceptions.IncorrectProfileValue:
        context.user_data.view.reg.warn.incorrect_location()
        return
    context.user_data.view.reg.ask_user_photos()
    return 6


def photos_handler_tg_photo(update: Update, context: CallbackContext, ):
    """Always returns None"""
    result_text = context.user_data.forms.new_user.handle_photo_tg_object(
        photo=update.effective_message.photo,
        media_group_id=update.effective_message.media_group_id,
    )
    if result_text == app.constants.Reg.PHOTO_ADDED_SUCCESS:
        context.user_data.view.reg.say_photo_added_success(keyboard=context.user_data.forms.new_user.current_keyboard, )
    elif result_text == app.constants.Reg.TOO_MANY_PHOTOS:
        context.user_data.view.reg.warn.too_many_photos(
            # TODO passing keyboard explicitly is poor design. Use forms.new_user.keyboard inside views
            keyboard=context.user_data.forms.new_user.current_keyboard,
            used_photos=len(context.user_data.forms.new_user.photos, ),
        )


def photos_handler_text(update: Update, context: CallbackContext, ):
    result_text = context.user_data.forms.new_user.handle_photo_text(text=update.effective_message.text, )
    if result_text == app.constants.Reg.PHOTOS_ADDED_SUCCESS:
        context.user_data.view.reg.say_photo_added_success(keyboard=context.user_data.forms.new_user.current_keyboard, )
    elif result_text == app.constants.Reg.TOO_MANY_PHOTOS:
        context.user_data.view.reg.warn.too_many_photos(
            keyboard=context.user_data.forms.new_user.current_keyboard,
            used_photos=len(context.user_data.forms.new_user.photos, ),
        )
    elif result_text == app.constants.Reg.PHOTOS_REMOVED_SUCCESS:
        context.user_data.view.reg.say_photos_removed_success(
            keyboard=context.user_data.forms.new_user.current_keyboard,
        )
    elif result_text == app.constants.Reg.NO_PHOTOS_TO_REMOVE:
        context.user_data.view.reg.warn.no_profile_photos()
    elif result_text == INCORRECT_FINISH_KEYWORD:
        context.user_data.view.warn.incorrect_finish()
    elif result_text == FINISH_KEYWORD:
        context.user_data.view.reg.ask_user_comment()
        return 7


def comment_handler(update: Update, context: CallbackContext, ):
    try:
        context.user_data.forms.new_user.handle_comment(text=update.message.text, )
    except app.exceptions.IncorrectProfileValue:
        context.user_data.view.reg.warn.comment_too_long(comment_len=len(update.message.text), )
        return
    context.user_data.view.reg.show_profile(profile=context.user_data.forms.new_user.profile, )
    return 8


def confirm_handler(update: Update, context: CallbackContext, ):
    # Create handler
    if update.message.text.lower().strip() != FINISH_KEYWORD.lower():
        context.user_data.view.reg.warn.incorrect_end_reg()
        return
    context.user_data.forms.new_user.create()
    context.user_data.view.reg.say_success_reg()
    return app.tg.ptb.utils.end_conversation()

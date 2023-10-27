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
from unittest.mock import ANY, patch
from typing import TYPE_CHECKING

import pytest
# noinspection PyPackageRequirements
from telegram import Update as tg_Update

import app.tg.ptb.handlers.reg
import app.generation
import app.tg.ptb.config
import app.tg.ptb.classes.users

import app.tg.ptb.forms.user

from tests.tg.ptb.functional.utils import get_text_cases

if TYPE_CHECKING:
    from unittest.mock import MagicMock

CLS_TO_TEST = app.tg.ptb.handlers.reg
EXCEPTION = app.exceptions.IncorrectProfileValue

"""Mock context automatically uses reset_mock() during tests"""


@pytest.fixture(autouse=True, )
def reset_mock_target(mock_context: MagicMock, ) -> None:
    if hasattr(mock_context.user_data.forms.new_user, 'reset_mock', ):  # First time is none rather than mock
        mock_context.user_data.forms.new_user.reset_mock()


def test_reg_entry_point(mock_context: MagicMock, tg_update_f: tg_Update, monkeypatch, ):
    # Execution
    result = CLS_TO_TEST.entry_point(_=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.view.reg.say_reg_hello.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result == 0


def test_reg_entry_point_handler(mock_context: MagicMock, tg_update_f: tg_Update, mock_ptb_new_user_f: MagicMock, ):
    # "return_value" to attach (make a child) future mock to mock_context
    with patch.object(
            app.tg.ptb.forms.user,
            'NewUser',
            autospec=True,
            return_value=mock_ptb_new_user_f,
    ) as mock_new_user_cls:
        result = CLS_TO_TEST.entry_point_handler(_=tg_update_f, context=mock_context, )
    # Checks
    mock_new_user_cls.assert_called_once_with(user=mock_context.user_data.current_user)
    assert mock_context.user_data.forms.new_user == mock_new_user_cls.return_value
    mock_context.user_data.view.reg.ask_user_name.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result == 1


def test_name_handler_incorrect(mock_context: MagicMock, tg_update_f: tg_Update, monkeypatch, ):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', 'foo')
    monkeypatch.setattr(mock_context.user_data.forms.new_user.handle_name, 'side_effect', EXCEPTION, )
    # Execution
    result = CLS_TO_TEST.name_handler(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_name.assert_called_once_with(text='foo')
    mock_context.user_data.view.reg.warn.incorrect_name.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1  # Total count of calls
    assert result is None


@pytest.mark.parametrize(
    argnames='text',
    argvalues=get_text_cases(texts=[app.generation.generator.gen_fullname()]),
)
def test_name_handler(mock_context: MagicMock, tg_update_f: tg_Update, monkeypatch, text: str, ):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
    # Execution
    result = CLS_TO_TEST.name_handler(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_name.assert_called_once_with(text=text)
    mock_context.user_data.view.reg.ask_user_goal.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result == 2


def test_goal_handler_incorrect(mock_context: MagicMock, tg_update_f: tg_Update, monkeypatch, ):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', 'foo')
    monkeypatch.setattr(mock_context.user_data.forms.new_user.handle_goal, 'side_effect', EXCEPTION, )
    # Execution
    result = CLS_TO_TEST.goal_handler(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_goal.assert_called_once_with(text='foo')
    mock_context.user_data.view.reg.warn.incorrect_goal.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1  # Total count of calls
    assert result is None


@pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=app.constants.Reg.REG_GOALS))
def test_goal_handler(mock_context: MagicMock, tg_update_f: tg_Update, text: str, monkeypatch, ):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
    # Execution
    result = CLS_TO_TEST.goal_handler(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_goal.assert_called_once_with(text=text)
    mock_context.user_data.view.reg.ask_user_gender.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1  # Total count of calls
    assert result == 3


def test_gender_handler_incorrect(mock_context: MagicMock, tg_update_f: tg_Update, monkeypatch, ):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', 'foo')
    monkeypatch.setattr(mock_context.user_data.forms.new_user.handle_gender, 'side_effect', EXCEPTION, )
    # Execution
    result = CLS_TO_TEST.gender_handler(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_gender.assert_called_once_with(text='foo')
    mock_context.user_data.view.reg.warn.incorrect_gender.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1  # Total count of calls
    assert result is None


@pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=app.constants.Reg.REG_GENDERS))
def test_gender_handler(mock_context: MagicMock, tg_update_f: tg_Update, text: str, monkeypatch, ):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
    # Execution
    result = CLS_TO_TEST.gender_handler(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_gender.assert_called_once_with(text=text)
    mock_context.user_data.view.reg.ask_user_age.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result == 4


def test_age_handler_incorrect(mock_context: MagicMock, tg_update_f: tg_Update, monkeypatch, ):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', 'foo')
    monkeypatch.setattr(mock_context.user_data.forms.new_user.handle_age, 'side_effect', EXCEPTION, )
    # Execution
    result = CLS_TO_TEST.age_handler(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_age.assert_called_once_with(text='foo')
    mock_context.user_data.view.reg.warn.incorrect_age.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result is None


@pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=['e1e0', 'sad4fs2', '99lk&^*']))
def test_age_handler(mock_context: MagicMock, tg_update_f: tg_Update, text: str, monkeypatch, ):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
    # Execution
    result = CLS_TO_TEST.age_handler(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_age.assert_called_once_with(text=text)
    mock_context.user_data.view.reg.ask_user_location.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result == 5


class TestLocationHandler:
    """location_handler"""

    @staticmethod
    def test_geo_incorrect(mock_context: MagicMock, tg_update_f: tg_Update, monkeypatch, ):
        monkeypatch.setattr(
            mock_context.user_data.forms.new_user.handle_location_geo, 'side_effect', app.exceptions.BadLocation
        )
        # Execution
        result = CLS_TO_TEST.location_handler_geo(update=tg_update_f, context=mock_context, )
        # Checks
        mock_context.user_data.forms.new_user.handle_location_geo.assert_called_once_with(
            location=tg_update_f.effective_message.location,
        )
        mock_context.user_data.view.reg.warn.incorrect_location.assert_called_once_with()
        assert len(mock_context.user_data.view.mock_calls) == 1
        assert len(mock_context.mock_calls) == 1
        assert result is None

    @staticmethod
    def test_geo_location_service_error(mock_context: MagicMock, tg_update_f: tg_Update, monkeypatch, ):
        exception = app.exceptions.LocationServiceError
        monkeypatch.setattr(mock_context.user_data.forms.new_user.handle_location_geo, 'side_effect', exception, )
        # Execution
        result = CLS_TO_TEST.location_handler_geo(update=tg_update_f, context=mock_context, )
        # Checks
        mock_context.user_data.forms.new_user.handle_location_geo.assert_called_once_with(
            location=tg_update_f.effective_message.location,
        )
        mock_context.user_data.view.location_service_error.assert_called_once_with()
        assert len(mock_context.user_data.view.mock_calls) == 1
        assert len(mock_context.mock_calls) == 1
        assert result is None

    @staticmethod
    def test_geo_success(mock_context: MagicMock, tg_update_f: tg_Update, monkeypatch, ):
        result = CLS_TO_TEST.location_handler_geo(update=tg_update_f, context=mock_context, )
        # Checks
        mock_context.user_data.forms.new_user.handle_location_geo.assert_called_once_with(
            location=tg_update_f.effective_message.location,
        )
        mock_context.user_data.view.reg.ask_user_photos.assert_called_once_with()
        assert len(mock_context.user_data.view.mock_calls) == 1
        assert len(mock_context.mock_calls) == 1
        assert result == 6

    @staticmethod
    def test_text_incorrect(mock_context: MagicMock, tg_update_f: tg_Update, monkeypatch, ):
        monkeypatch.setattr(mock_context.user_data.forms.new_user.handle_location_text, 'side_effect', EXCEPTION, )
        # Execution
        result = CLS_TO_TEST.location_handler_text(update=tg_update_f, context=mock_context, )
        # Checks
        mock_context.user_data.forms.new_user.handle_location_text.assert_called_once_with(
            text=tg_update_f.effective_message.text,
        )
        mock_context.user_data.view.reg.warn.incorrect_location.assert_called_once_with()
        assert len(mock_context.user_data.view.mock_calls) == 1
        assert len(mock_context.mock_calls) == 1
        assert result is None


@pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=['foo']))
def test_text_success(mock_context: MagicMock, tg_update_f: tg_Update, text: str, monkeypatch, ):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
    # Execution
    result = CLS_TO_TEST.location_handler_text(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_location_text.assert_called_once_with(
        text=tg_update_f.effective_message.text,
    )
    mock_context.user_data.view.reg.ask_user_photos.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result == 6


def test_photos_handler_tg_photo_success(
        tg_update_f: tg_Update,
        mock_context: MagicMock,
        monkeypatch,
):
    return_value = app.constants.Reg.PHOTO_ADDED_SUCCESS
    monkeypatch.setattr(mock_context.user_data.forms.new_user.handle_photo_tg_object, 'return_value', return_value, )
    # Execution
    result = CLS_TO_TEST.photos_handler_tg_photo(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_photo_tg_object.assert_called_once_with(
        photo=tg_update_f.effective_message.photo,
        media_group_id=tg_update_f.effective_message.media_group_id,
    )
    keyboard = mock_context.user_data.forms.new_user.current_keyboard
    mock_context.user_data.view.reg.say_photo_added_success.assert_called_once_with(keyboard=keyboard, )
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result is None  # Same state because still waiting for photos


def test_photos_handler_tg_photo_too_many_photos(
        tg_update_f: tg_Update,
        mock_context: MagicMock,
        monkeypatch,
):
    return_value = app.constants.Reg.TOO_MANY_PHOTOS
    monkeypatch.setattr(mock_context.user_data.forms.new_user.handle_photo_tg_object, 'return_value', return_value, )
    # Execution
    result = CLS_TO_TEST.photos_handler_tg_photo(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_photo_tg_object.assert_called_once_with(
        photo=tg_update_f.effective_message.photo,
        media_group_id=tg_update_f.effective_message.media_group_id,
    )
    mock_context.user_data.view.reg.warn.too_many_photos.assert_called_once_with(
        keyboard=mock_context.user_data.forms.new_user.current_keyboard,
        used_photos=len(mock_context.user_data.forms.new_user.photos),
    )
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result is None  # Same state because still waiting for photos


@pytest.mark.parametrize(argnames='media_group_id', argvalues=['1', '2'])
def test_photos_handler_tg_album_photo(
        tg_update_f: tg_Update,
        mock_context: MagicMock,
        media_group_id: str,
        monkeypatch,
):
    monkeypatch.setattr(tg_update_f.effective_message, 'media_group_id', media_group_id)
    # Execution
    result = CLS_TO_TEST.photos_handler_tg_photo(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_photo_tg_object.assert_called_once_with(
        photo=tg_update_f.effective_message.photo,
        media_group_id=tg_update_f.effective_message.media_group_id,
    )
    assert len(mock_context.user_data.view.mock_calls) == 0
    assert len(mock_context.mock_calls) == 0
    assert result is None  # Same state because still waiting for photos


def test_photos_handler_text_account_photos(
        tg_update_f: tg_Update,
        mock_context: MagicMock,
        monkeypatch,
):
    """app.constants.FINISH Should be in another test because will lead to next stage"""
    return_value = app.constants.Reg.PHOTOS_ADDED_SUCCESS
    monkeypatch.setattr(mock_context.user_data.forms.new_user.handle_photo_text, 'return_value', return_value, )
    # Execution
    result = CLS_TO_TEST.photos_handler_text(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_photo_text.assert_called_once_with(text=ANY)
    mock_context.user_data.view.reg.say_photo_added_success.assert_called_once_with(
        keyboard=mock_context.user_data.forms.new_user.current_keyboard,
    )
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result is None


def test_photos_handler_text_incorrect(
        tg_update_f: tg_Update,
        mock_context: MagicMock,
        monkeypatch,
):
    """app.constants.FINISH Should be in another test because will lead to next stage"""
    return_value = app.constants.Shared.Warn.INCORRECT_FINISH
    monkeypatch.setattr(mock_context.user_data.forms.new_user.handle_photo_text, 'return_value', return_value, )
    # Execution
    result = CLS_TO_TEST.photos_handler_text(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_photo_text.assert_called_once_with(
        text=tg_update_f.effective_message.text,
    )
    mock_context.user_data.view.warn.incorrect_finish.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result is None


def test_photos_handler_text_no_photos_to_remove(
        tg_update_f: tg_Update,
        mock_context: MagicMock,
        monkeypatch,
):
    return_value = app.constants.Reg.NO_PHOTOS_TO_REMOVE
    monkeypatch.setattr(mock_context.user_data.forms.new_user.handle_photo_text, 'return_value', return_value, )
    # Execution
    result = CLS_TO_TEST.photos_handler_text(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_photo_text.assert_called_once_with(text=ANY)
    mock_context.user_data.view.reg.warn.no_profile_photos.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result is None  # Same state because still waiting for photos


def test_photos_handler_text_photos_removed_success(
        tg_update_f: tg_Update,
        mock_context: MagicMock,
        monkeypatch,
):
    return_value = app.constants.Reg.PHOTOS_REMOVED_SUCCESS
    monkeypatch.setattr(mock_context.user_data.forms.new_user.handle_photo_text, 'return_value', return_value, )
    # Execution
    result = CLS_TO_TEST.photos_handler_text(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_photo_text.assert_called_once_with(text=ANY)
    keyboard = mock_context.user_data.forms.new_user.current_keyboard
    mock_context.user_data.view.reg.say_photos_removed_success.assert_called_once_with(keyboard=keyboard)
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result is None  # Same state because still waiting for photos


def test_photos_handler_text_too_many_photos(
        tg_update_f: tg_Update,
        mock_context: MagicMock,
):
    with patch.object(
            mock_context.user_data.forms.new_user.handle_photo_text, 'return_value', app.constants.Reg.TOO_MANY_PHOTOS
    ):
        # Execution
        result = CLS_TO_TEST.photos_handler_text(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_photo_text.assert_called_once_with(text=ANY)
    keyboard = mock_context.user_data.forms.new_user.current_keyboard
    mock_context.user_data.view.reg.warn.too_many_photos.assert_called_once_with(keyboard=keyboard, used_photos=0, )
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result is None  # Same state because still waiting for photos


def test_photos_handler_finish(tg_update_f: tg_Update, mock_context: MagicMock, monkeypatch, ):
    monkeypatch.setattr(
        mock_context.user_data.forms.new_user.handle_photo_text,
        'return_value',
        app.constants.Shared.Words.FINISH,
    )
    # Execution
    result = CLS_TO_TEST.photos_handler_text(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_photo_text.assert_called_once_with(text=ANY)
    mock_context.user_data.view.reg.ask_user_comment.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result == 7


def test_comment_handler_incorrect(
        tg_update_f: tg_Update,
        mock_context: MagicMock,
        monkeypatch,
):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', 'foo')  # To apply len method on string, was None
    monkeypatch.setattr(mock_context.user_data.forms.new_user.handle_comment, 'side_effect', EXCEPTION, )
    # Execution
    result = CLS_TO_TEST.comment_handler(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_comment.assert_called_once_with(
        text=tg_update_f.message.text
    )
    mock_context.user_data.view.reg.warn.comment_too_long.assert_called_once_with(
        comment_len=len(tg_update_f.effective_message.text),
    )
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result is None


def test_comment_handler(
        tg_update_f: tg_Update,
        mock_context: MagicMock,
        monkeypatch,
):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', app.generation.generator.gen_comment())
    # Execution
    result = CLS_TO_TEST.comment_handler(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.handle_comment.assert_called_once_with(
        text=tg_update_f.message.text,
)
    profile = mock_context.user_data.forms.new_user.profile
    mock_context.user_data.view.reg.show_profile.assert_called_once_with(profile=profile, )
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result == 8


def test_confirm_handler_incorrect(
        tg_update_f: tg_Update,
        mock_context: MagicMock,
        monkeypatch,
):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', 'foo')
    # Execution
    result = CLS_TO_TEST.confirm_handler(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.view.reg.warn.incorrect_end_reg.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result is None


@pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=[app.constants.Shared.Words.FINISH], ))
def test_confirm_handler(
        tg_update_f: tg_Update,
        mock_context: MagicMock,
        text: str,
        monkeypatch,
):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
    # Execution
    result = CLS_TO_TEST.confirm_handler(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.forms.new_user.create.assert_called_once_with()
    mock_context.user_data.view.reg.say_success_reg.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert len(mock_context.mock_calls) == 1
    assert result == -1

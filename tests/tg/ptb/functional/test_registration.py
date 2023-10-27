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

import pytest
# noinspection PyPackageRequirements
from telegram import (
    Update as tg_Update,
    Location as tg_Location,
    PhotoSize as tg_PhotoSize,
)
# noinspection PyPackageRequirements
from telegram.ext import Dispatcher as tg_Dispatcher

import app.generation
import app.tg.ptb.config
import app.tg.ptb.handlers_definition

from tests.tg.ptb.functional.utils import set_command_to_tg_message, get_text_cases, cancel_body

CLS_TO_TEST = app.tg.ptb.handlers_definition.RegistrationCH


def test_reg_entry_point(tg_update_f: tg_Update, tg_dispatcher: tg_Dispatcher, ):
    assert (tg_update_f.effective_chat.id, tg_update_f.effective_user.id) not in CLS_TO_TEST.CH.conversations
    set_command_to_tg_message(tg_message=tg_update_f.effective_message, cmd_text=app.tg.ptb.config.REG_S, )
    tg_dispatcher.process_update(update=tg_update_f, )
    CLS_TO_TEST.entry_point.callback.assert_called_once()


@pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=['foo']))
def test_reg_entry_point_handler(
        tg_update_f: tg_Update,
        tg_dispatcher: tg_Dispatcher,
        text: str,
        monkeypatch,
):
    CLS_TO_TEST.CH.conversations[(tg_update_f.effective_chat.id, tg_update_f.effective_user.id)] = 0
    monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
    tg_dispatcher.process_update(update=tg_update_f, )
    CLS_TO_TEST.entry_point_handler.callback.assert_called_once()
    CLS_TO_TEST.entry_point_handler.callback.reset_mock()


@pytest.mark.parametrize(
    argnames='text',
    argvalues=get_text_cases(texts=[app.generation.generator.gen_fullname()]),
)
def test_user_name_handler(
        tg_update_f: tg_Update,
        tg_dispatcher: tg_Dispatcher,
        text: str,
        monkeypatch,
):
    CLS_TO_TEST.name_handler.callback.reset_mock()
    CLS_TO_TEST.CH.conversations[(tg_update_f.effective_chat.id, tg_update_f.effective_user.id)] = 1
    monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
    tg_dispatcher.process_update(update=tg_update_f, )
    CLS_TO_TEST.name_handler.callback.assert_called_once()


@pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=app.constants.Reg.REG_GOALS))
def test_user_goal_handler(
        tg_update_f: tg_Update,
        tg_dispatcher: tg_Dispatcher,
        text: str,
        monkeypatch,
):
    CLS_TO_TEST.goal_handler.callback.reset_mock()
    CLS_TO_TEST.CH.conversations[(tg_update_f.effective_chat.id, tg_update_f.effective_user.id)] = 2
    monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
    tg_dispatcher.process_update(update=tg_update_f, )
    CLS_TO_TEST.goal_handler.callback.assert_called_once()


@pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=app.constants.Reg.REG_GENDERS))
def test_user_gender_handler(
        tg_update_f: tg_Update,
        tg_dispatcher: tg_Dispatcher,
        text: str,
        monkeypatch,
):
    CLS_TO_TEST.gender_handler.callback.reset_mock()
    CLS_TO_TEST.CH.conversations[(tg_update_f.effective_chat.id, tg_update_f.effective_user.id)] = 3
    monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
    tg_dispatcher.process_update(update=tg_update_f, )
    CLS_TO_TEST.gender_handler.callback.assert_called_once()


@pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=['e1e0', 'sad4fs2', '99lk&^*']))
def test_user_age_handler(
        tg_update_f: tg_Update,
        tg_dispatcher: tg_Dispatcher,
        text: str,
        monkeypatch,
):
    CLS_TO_TEST.age_handler.callback.reset_mock()
    CLS_TO_TEST.CH.conversations[(tg_update_f.effective_chat.id, tg_update_f.effective_user.id)] = 4
    monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
    tg_dispatcher.process_update(update=tg_update_f, )
    CLS_TO_TEST.age_handler.callback.assert_called_once()


@pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=['foo']))
def test_user_location_handler_text(
        tg_update_f: tg_Update,
        tg_dispatcher: tg_Dispatcher,
        text: str,
        monkeypatch,
):
    CLS_TO_TEST.location_handler_text.callback.reset_mock()
    CLS_TO_TEST.CH.conversations[(tg_update_f.effective_chat.id, tg_update_f.effective_user.id)] = 5
    monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
    tg_dispatcher.process_update(update=tg_update_f, )
    CLS_TO_TEST.location_handler_text.callback.assert_called_once()


def test_user_location_handler_geo(
        tg_update_f: tg_Update,
        tg_dispatcher: tg_Dispatcher,
        monkeypatch,
):
    CLS_TO_TEST.location_handler_geo.callback.reset_mock()
    CLS_TO_TEST.CH.conversations[(tg_update_f.effective_chat.id, tg_update_f.effective_user.id)] = 5
    monkeypatch.setattr(tg_update_f.effective_message, 'location', tg_Location(longitude=45, latitude=45))
    tg_dispatcher.process_update(update=tg_update_f, )
    CLS_TO_TEST.location_handler_geo.callback.assert_called_once()


def test_user_photos_handler_tg_photo(
        tg_update_f: tg_Update,
        tg_dispatcher: tg_Dispatcher,
        tg_ptb_photo_s: list[tg_PhotoSize],
        monkeypatch,
):
    CLS_TO_TEST.CH.conversations[(tg_update_f.effective_chat.id, tg_update_f.effective_user.id)] = 6
    monkeypatch.setattr(tg_update_f.effective_message, 'photo', tg_ptb_photo_s, )
    tg_dispatcher.process_update(update=tg_update_f, )
    CLS_TO_TEST.photos_handler_photo.callback.assert_called_once()


@pytest.mark.parametrize(argnames='media_group_id', argvalues=['1', '2'])
def test_user_photos_handler_album(
        tg_update_f: tg_Update,
        tg_dispatcher: tg_Dispatcher,
        media_group_id: str,
        tg_ptb_photo_s: list[tg_PhotoSize],
        monkeypatch,
):
    CLS_TO_TEST.photos_handler_photo.callback.reset_mock()
    CLS_TO_TEST.CH.conversations[(tg_update_f.effective_chat.id, tg_update_f.effective_user.id)] = 6
    monkeypatch.setattr(tg_update_f.effective_message, 'photo', tg_ptb_photo_s, )
    monkeypatch.setattr(tg_update_f.effective_message, 'media_group_id', media_group_id, )
    tg_dispatcher.process_update(update=tg_update_f, )
    CLS_TO_TEST.photos_handler_photo.callback.assert_called_once()


@pytest.mark.parametrize(
    argnames='text',
    argvalues=[app.constants.Reg.Buttons.USE_ACCOUNT_PHOTOS, app.constants.Reg.Buttons.REMOVE_PHOTOS],
)
def test_user_photos_handler_text(
        tg_update_f: tg_Update,
        tg_dispatcher: tg_Dispatcher,
        monkeypatch,
        text: str,
):
    CLS_TO_TEST.photos_handler_text.callback.reset_mock()
    CLS_TO_TEST.CH.conversations[(tg_update_f.effective_chat.id, tg_update_f.effective_user.id)] = 6
    monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
    tg_dispatcher.process_update(update=tg_update_f, )
    CLS_TO_TEST.photos_handler_text.callback.assert_called_once()


@pytest.mark.parametrize(
    argnames='text',
    argvalues=get_text_cases(texts=[app.generation.generator.gen_comment() for _ in range(5)], )
)
def test_user_comment_handler(
        tg_update_f: tg_Update,
        tg_dispatcher: tg_Dispatcher,
        monkeypatch,
        text: str,
):
    CLS_TO_TEST.comment_handler.callback.reset_mock()
    CLS_TO_TEST.CH.conversations[(tg_update_f.effective_chat.id, tg_update_f.effective_user.id)] = 7
    monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
    tg_dispatcher.process_update(update=tg_update_f, )
    CLS_TO_TEST.comment_handler.callback.assert_called_once()


@pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=[app.constants.Shared.Words.FINISH], ))
def test_user_confirm_handler(
        tg_update_f: tg_Update,
        tg_dispatcher: tg_Dispatcher,
        monkeypatch,
        text: str,
):
    CLS_TO_TEST.confirm_handler.callback.reset_mock()
    CLS_TO_TEST.CH.conversations[(tg_update_f.effective_chat.id, tg_update_f.effective_user.id)] = 8
    monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
    tg_dispatcher.process_update(update=tg_update_f, )
    CLS_TO_TEST.confirm_handler.callback.assert_called_once()


def test_cancel(
        tg_update_f: tg_Update,
        tg_dispatcher: tg_Dispatcher,
        monkeypatch,
):
    cancel_body(
        update=tg_update_f,
        dispatcher=tg_dispatcher,
        ch=CLS_TO_TEST.CH,
        callback=CLS_TO_TEST.cancel.callback,
        monkeypatch=monkeypatch,
    )

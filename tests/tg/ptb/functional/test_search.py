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

import pytest
# noinspection PyPackageRequirements
from telegram import Update as tg_Update
# noinspection PyPackageRequirements
from telegram.ext import Dispatcher as tg_Dispatcher

from app.tg.ptb.classes.matches import Matcher
import app.tg.ptb.config
import app.tg.ptb.handlers_definition

from tests.tg.ptb.functional.utils import set_command_to_tg_message, get_text_cases, cancel_body

if TYPE_CHECKING:
    pass

CLS_TO_TEST = app.tg.ptb.handlers_definition.SearchCH


def test_entry_point(tg_update_f: tg_Update, tg_dispatcher: tg_Dispatcher, ):
    CLS_TO_TEST.CH.conversations.pop((tg_update_f.effective_chat.id, tg_update_f.effective_user.id), None)
    set_command_to_tg_message(tg_message=tg_update_f.effective_message, cmd_text=app.tg.ptb.config.SEARCH_S)
    tg_dispatcher.process_update(update=tg_update_f, )
    CLS_TO_TEST.entry_point.callback.assert_called_once()


@pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=['foo']))
def test_entry_point_handler(
        tg_update_f: tg_Update,
        tg_dispatcher: tg_Dispatcher,
        text: str,
        monkeypatch,
):
    CLS_TO_TEST.entry_point_handler.callback.reset_mock()
    CLS_TO_TEST.CH.conversations[(tg_update_f.effective_chat.id, tg_update_f.effective_user.id)] = 0
    monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
    tg_dispatcher.process_update(update=tg_update_f, )
    CLS_TO_TEST.entry_point_handler.callback.assert_called_once()


@pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=app.constants.Search.TARGET_GOALS))
def test_target_goal_handler(
        tg_update_f: tg_Update,
        tg_dispatcher: tg_Dispatcher,
        text: str,
        monkeypatch,
):
    CLS_TO_TEST.goal_handler.callback.reset_mock()
    CLS_TO_TEST.CH.conversations[(tg_update_f.effective_chat.id, tg_update_f.effective_user.id)] = 1
    monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
    tg_dispatcher.process_update(update=tg_update_f, )
    CLS_TO_TEST.goal_handler.callback.assert_called_once()


@pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=app.constants.Search.TARGET_GENDERS))
def test_target_gender_handler(
        tg_update_f: tg_Update,
        tg_dispatcher: tg_Dispatcher,
        text: str,
        monkeypatch,
):
    CLS_TO_TEST.gender_handler.callback.reset_mock()
    CLS_TO_TEST.CH.conversations[(tg_update_f.effective_chat.id, tg_update_f.effective_user.id)] = 2
    monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
    tg_dispatcher.process_update(update=tg_update_f, )
    CLS_TO_TEST.gender_handler.callback.assert_called_once()


@pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=['e1e0', 'sad4fs2', '99lk&^*']))
def test_target_age_handler(
        tg_update_f: tg_Update,
        tg_dispatcher: tg_Dispatcher,
        text: str,
        monkeypatch,
):
    CLS_TO_TEST.age_handler.callback.reset_mock()
    CLS_TO_TEST.CH.conversations[(tg_update_f.effective_chat.id, tg_update_f.effective_user.id)] = 3
    monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
    tg_dispatcher.process_update(update=tg_update_f, )
    CLS_TO_TEST.age_handler.callback.assert_called_once()


@pytest.mark.parametrize('checkbox', Matcher.Filters.Checkbox.__annotations__)
@pytest.mark.parametrize('value', [1, -1])
def test_checkbox_cbk_handler_success(
        tg_update_f: tg_Update,
        tg_dispatcher: tg_Dispatcher,
        monkeypatch,
        checkbox: str,
        value: int,
):
    CLS_TO_TEST.checkbox_cbk_handler.callback.reset_mock()
    CLS_TO_TEST.CH.conversations[(tg_update_f.effective_chat.id, tg_update_f.effective_user.id)] = 4
    monkeypatch.setattr(tg_update_f.callback_query, 'data', f'{app.tg.ptb.config.CHECKBOX_CBK_S} {checkbox} {value}')
    tg_dispatcher.process_update(update=tg_update_f, )
    CLS_TO_TEST.checkbox_cbk_handler.callback.assert_called_once()


@pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=['foo']))
def test_target_checkboxes_handler(
        tg_update_f: tg_Update,
        tg_dispatcher: tg_Dispatcher,
        text: str,
        monkeypatch,
):
    CLS_TO_TEST.checkboxes_handler.callback.reset_mock()
    CLS_TO_TEST.CH.conversations[(tg_update_f.effective_chat.id, tg_update_f.effective_user.id)] = 4
    monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
    tg_dispatcher.process_update(update=tg_update_f, )
    CLS_TO_TEST.checkboxes_handler.callback.assert_called_once()


@pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=app.constants.Search.TARGET_SHOW_CHOICE))
def test_target_confirm_handler(
        tg_update_f: tg_Update,
        tg_dispatcher: tg_Dispatcher,
        text: str,
        monkeypatch,
):
    CLS_TO_TEST.confirm_handler.callback.reset_mock()
    CLS_TO_TEST.CH.conversations[(tg_update_f.effective_chat.id, tg_update_f.effective_user.id)] = 5
    monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
    tg_dispatcher.process_update(update=tg_update_f, )
    CLS_TO_TEST.confirm_handler.callback.assert_called_once()


@pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=[app.constants.Search.Buttons.SHOW_MORE]))
def test_target_confirm_handler_show_match(
        tg_update_f: tg_Update,
        tg_dispatcher: tg_Dispatcher,
        text: str,
        monkeypatch,
):
    CLS_TO_TEST.show_match_handler.callback.reset_mock()
    CLS_TO_TEST.CH.conversations[(tg_update_f.effective_chat.id, tg_update_f.effective_user.id)] = 6
    monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
    tg_dispatcher.process_update(update=tg_update_f, )
    CLS_TO_TEST.show_match_handler.callback.assert_called_once()


@pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=[app.constants.Shared.Words.COMPLETE]))
def test_target_show_match_handler(
        tg_update_f: tg_Update,
        tg_dispatcher: tg_Dispatcher,
        text: str,
        monkeypatch,
):
    CLS_TO_TEST.show_match_handler.callback.reset_mock()
    CLS_TO_TEST.CH.conversations[(tg_update_f.effective_chat.id, tg_update_f.effective_user.id)] = 6
    monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
    tg_dispatcher.process_update(update=tg_update_f, )
    CLS_TO_TEST.show_match_handler.callback.assert_called_once()


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

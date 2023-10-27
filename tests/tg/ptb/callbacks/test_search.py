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
from unittest.mock import patch

import pytest
# noinspection PyPackageRequirements
from telegram import Update as tg_Update

from app.exceptions import NoVotes, NoCovotes, IncorrectProfileValue
from app.tg.ptb.classes.matches import Matcher
import app.tg.ptb.config
import app.tg.ptb.handlers.search

from tests.tg.ptb.functional.utils import get_text_cases

import app.tg.ptb.forms

if TYPE_CHECKING:
    import app.models.users
    from unittest.mock import MagicMock

"""Mock context automatically uses reset_mock() during tests"""


@pytest.fixture(autouse=True, )
def reset_mock_target(mock_context: MagicMock, ) -> None:
    if hasattr(mock_context.user_data.forms.target, 'reset_mock', ):  # First time is none rather than mock
        mock_context.user_data.forms.target.reset_mock()


@pytest.fixture()
def patched_target_cls(mock_ptb_target: MagicMock, ):
    with patch.object(
            app.tg.ptb.forms.user,
            'Target',
            autospec=True,
            return_value=mock_ptb_target,
    ) as mock:
        yield mock


def test_entry_point(mock_context: MagicMock, tg_update_f: tg_Update, monkeypatch, ):
    result = app.tg.ptb.handlers.search.entry_point(_=tg_update_f, context=mock_context, )
    mock_context.user_data.view.search.say_search_hello.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert result == 0


def test_entry_point_handler_no_votes(
        mock_context: MagicMock,
        tg_update_f: tg_Update,
        patched_target_cls: MagicMock,
        monkeypatch,
):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', 'foo')  # Any text is ok
    monkeypatch.setattr(patched_target_cls.return_value.handle_start_search, 'side_effect', NoVotes, )
    result = app.tg.ptb.handlers.search.entry_point_handler(update=tg_update_f, context=mock_context, )
    # Checks
    patched_target_cls.assert_called_once_with(user=mock_context.user_data.current_user, )
    mock_context.user_data.forms.target.handle_start_search.assert_called_once_with(
        text=tg_update_f.effective_message.text
    )
    mock_context.user_data.view.search.no_votes.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert result == -1


def test_entry_point_handler_no_covotes(
        mock_context: MagicMock,
        tg_update_f: tg_Update,
        patched_target_cls: MagicMock,
        monkeypatch,
):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', 'foo')  # Any text is ok
    monkeypatch.setattr(patched_target_cls.return_value.handle_start_search, 'side_effect', NoCovotes, )
    # Execution
    result = app.tg.ptb.handlers.search.entry_point_handler(update=tg_update_f, context=mock_context, )
    # Checks
    patched_target_cls.assert_called_once_with(user=mock_context.user_data.current_user, )
    mock_context.user_data.forms.target.handle_start_search.assert_called_once_with(
        text=tg_update_f.effective_message.text,
    )
    mock_context.user_data.view.search.no_covotes.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert result == -1


def test_entry_point_handler(
        mock_context: MagicMock,
        tg_update_f: tg_Update,
        patched_target_cls: MagicMock,
        monkeypatch,
):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', 'foo')  # Any text is ok
    # Execution
    result = app.tg.ptb.handlers.search.entry_point_handler(update=tg_update_f, context=mock_context, )
    # Checks
    patched_target_cls.assert_called_once_with(user=mock_context.user_data.current_user, )
    mock_context.user_data.forms.target.handle_start_search.assert_called_once_with(
        text=tg_update_f.effective_message.text,
    )
    mock_context.user_data.view.search.ask_target_goal.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert result == 1


def test_goal_handler_incorrect(mock_context: MagicMock, tg_update_f: tg_Update, monkeypatch, patched_target_cls):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', 'foo')
    mock_handle_goal = mock_context.user_data.forms.target.handle_goal
    monkeypatch.setattr(mock_handle_goal, 'side_effect', IncorrectProfileValue)
    # Execution
    result = app.tg.ptb.handlers.search.goal_handler(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.forms.target.handle_goal.assert_called_once_with(text=tg_update_f.effective_message.text, )
    mock_context.user_data.view.search.warn.incorrect_target_goal.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert result is None


@pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=app.constants.Search.TARGET_GOALS))
def test_goal_handler(mock_context: MagicMock, tg_update_f: tg_Update, text: str, monkeypatch, mock_ptb_target):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
    # Execution
    result = app.tg.ptb.handlers.search.goal_handler(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.forms.target.handle_goal.assert_called_once_with(text=text)
    mock_context.user_data.view.search.ask_target_gender.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert result == 2


def test_gender_handler_incorrect(mock_context: MagicMock, tg_update_f: tg_Update, monkeypatch, ):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', 'foo')
    mock_handle_gender = mock_context.user_data.forms.target.handle_gender
    monkeypatch.setattr(mock_handle_gender, 'side_effect', IncorrectProfileValue)
    # Execution
    result = app.tg.ptb.handlers.search.gender_handler(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.forms.target.handle_gender.assert_called_once_with(
        text=tg_update_f.effective_message.text,
    )
    mock_context.user_data.view.search.warn.incorrect_target_gender.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert result is None


@pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=app.constants.Search.TARGET_GENDERS))
def test_gender_handler(mock_context: MagicMock, tg_update_f: tg_Update, text: str, monkeypatch, ):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
    # Execution
    result = app.tg.ptb.handlers.search.gender_handler(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.forms.target.handle_gender.assert_called_once_with(
        text=tg_update_f.effective_message.text,
    )
    mock_context.user_data.view.search.ask_target_age.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert result == 3


def test_age_handler_incorrect(mock_context: MagicMock, tg_update_f: tg_Update, monkeypatch, ):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', 'foo')
    mock_handle_age = mock_context.user_data.forms.target.handle_age
    monkeypatch.setattr(mock_handle_age, 'side_effect', IncorrectProfileValue)
    # Execution
    result = app.tg.ptb.handlers.search.age_handler(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.forms.target.handle_age.assert_called_once_with(
        text=tg_update_f.effective_message.text,
    )
    mock_context.user_data.view.search.warn.incorrect_target_age.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert result is None


@pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=['e1e0', 'sad4fs2', '99lk&^*']))
def test_age_handler(mock_context: MagicMock, tg_update_f: tg_Update, text: str, monkeypatch, ):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
    # Execution
    result = app.tg.ptb.handlers.search.age_handler(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.forms.target.handle_age.assert_called_once_with(
        text=tg_update_f.effective_message.text,
    )
    mock_context.user_data.view.search.show_target_checkboxes.assert_called_once_with(
        target=mock_context.user_data.forms.target,
    )
    mock_context.user_data.view.search.ask_confirm.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 2  # Need 2 calls for logic
    assert result == 4


def test_checkboxes_handler_no_matches_with_filters(mock_context: MagicMock, tg_update_f: tg_Update, monkeypatch, ):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', 'foo')
    with patch.object(mock_context.user_data.current_user.matcher.matches, 'all', [], ):
        result = app.tg.ptb.handlers.search.checkboxes_handler(_=tg_update_f, context=mock_context, )
    mock_context.user_data.current_user.matcher.make_search.assert_called_once_with()
    mock_context.user_data.view.search.no_matches_with_filters.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert result == -1


def test_checkboxes_handler(mock_context: MagicMock, tg_update_f: tg_Update, monkeypatch, ):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', 'foo', )
    # Execution
    with patch.object(mock_context.user_data.current_user.matcher.matches, 'all', ['foo', ], ):
        result = app.tg.ptb.handlers.search.checkboxes_handler(_=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.current_user.matcher.make_search.assert_called_once_with()
    matches = mock_context.user_data.current_user.matcher.matches
    mock_context.user_data.view.search.ask_which_matches_show.assert_called_once_with(matches=matches, )
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert result == 5


def test_match_type_handler_incorrect(mock_context: MagicMock, tg_update_f: tg_Update, monkeypatch, ):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', 'foo')
    mock_handle_show_option = mock_context.user_data.forms.target.handle_show_option
    monkeypatch.setattr(mock_handle_show_option, 'side_effect', IncorrectProfileValue)
    # Execution
    result = app.tg.ptb.handlers.search.match_type_handler(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.forms.target.handle_show_option.assert_called_once_with(
        text=tg_update_f.effective_message.text,
    )
    mock_context.user_data.view.search.warn.incorrect_show_option.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert result is None


def test_match_type_handler_no_more_matches(mock_context: MagicMock, tg_update_f: tg_Update, monkeypatch, ):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', app.constants.Search.Buttons.SHOW_ALL)
    monkeypatch.setattr(mock_context.user_data.current_user.matcher.get_match, 'return_value', None)
    # Execution
    result = app.tg.ptb.handlers.search.match_type_handler(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.current_user.matcher.get_match.assert_called_once_with()
    mock_context.user_data.view.search.no_more_matches.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert result == -1


@pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=app.constants.Search.TARGET_SHOW_CHOICE))
def test_match_type_handler(mock_context: MagicMock, tg_update_f: tg_Update, text: str, monkeypatch, ):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
    # Execution
    result = app.tg.ptb.handlers.search.match_type_handler(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.current_user.matcher.get_match.assert_called_once_with()
    mock_context.user_data.view.search.here_match.assert_called_once_with(
        stats=mock_context.user_data.current_user.matcher.get_match.return_value.stats,
    )
    mock_context.user_data.current_user.matcher.get_match.return_value.show.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert result


def test_show_match_handler_incorrect(mock_context: MagicMock, tg_update_f: tg_Update, monkeypatch, ):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', 'foo')
    # Execution
    result = app.tg.ptb.handlers.search.show_match_handler(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.view.search.warn.incorrect_show_more_option.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert result is None


def test_show_match_handler_no_more_matches(
        mock_context: MagicMock,
        tg_update_f: tg_Update,
        monkeypatch,
):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', app.constants.Search.Buttons.SHOW_MORE)
    monkeypatch.setattr(mock_context.user_data.current_user.matcher.get_match, 'return_value', None)
    # Execution
    result = app.tg.ptb.handlers.search.show_match_handler(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.view.search.no_more_matches.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert result == -1


@pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=[app.constants.Shared.Words.COMPLETE]))
def test_show_match_handler_complete(mock_context: MagicMock, tg_update_f: tg_Update, text: str, monkeypatch, ):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
    # Execution
    result = app.tg.ptb.handlers.search.show_match_handler(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.view.search.say_search_goodbye.assert_called_once_with()
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert result == -1


def test_show_match_handler(mock_context: MagicMock, tg_update_f: tg_Update, monkeypatch, ):
    monkeypatch.setattr(tg_update_f.effective_message, 'text', app.constants.Search.Buttons.SHOW_MORE)
    # Execution
    result = app.tg.ptb.handlers.search.show_match_handler(update=tg_update_f, context=mock_context, )
    # Checks
    mock_context.user_data.current_user.matcher.get_match.assert_called_once_with()
    mock_context.user_data.current_user.matcher.get_match.return_value.show.assert_called_once_with()
    mock_context.user_data.view.search.here_match.assert_called_once_with(
        stats=mock_context.user_data.current_user.matcher.get_match.return_value.stats,
    )
    assert len(mock_context.user_data.view.mock_calls) == 1
    assert result is None


@pytest.mark.parametrize('checkbox', Matcher.Filters.Checkbox.__annotations__)
def test_checkbox_cbk_handler(
        mock_context: MagicMock,
        tg_update_f: tg_Update,
        checkbox: str,
        monkeypatch,
):
    monkeypatch.setattr(tg_update_f.callback_query, 'data', f'{app.tg.ptb.config.CHECKBOX_CBK_S} {checkbox}')
    with patch.object(tg_update_f.callback_query, 'answer', ) as mock_answer:
        app.tg.ptb.handlers.search.checkbox_cbk_handler(update=tg_update_f, context=mock_context, )
    mock_context.user_data.view.search.update_target_checkboxes_keyboard(
        message_to_update=tg_update_f.effective_message,
        target=mock_context.user_data.forms.target,
    )
    mock_answer.assert_called_once_with()

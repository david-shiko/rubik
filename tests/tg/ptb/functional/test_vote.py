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

import pytest
# noinspection PyPackageRequirements
from telegram import Update as tg_Update
# noinspection PyPackageRequirements
from telegram.ext import Dispatcher as tg_Dispatcher

import app.tg.ptb.config
import app.tg.ptb.handlers_definition
from tests.tg.ptb.functional.utils import get_text_cases


class TestPublicVoteCbkHandler:
    @staticmethod
    @pytest.mark.parametrize(
        argnames='cbk_data', argvalues=[
            *get_text_cases(texts=[app.tg.ptb.config.PUBLIC_VOTE_CBK_S], lower=False),
            *get_text_cases(texts=['foo', 'bar egg'])
        ]
        )
    def test_buttons_not_triggered(
            tg_update_f: tg_Update,
            tg_dispatcher: tg_Dispatcher,
            cbk_data: str,
            monkeypatch,
    ):
        monkeypatch.setattr(tg_update_f.callback_query, 'data', cbk_data)
        tg_dispatcher.process_update(update=tg_update_f)
        app.tg.ptb.handlers_definition.accept_public_vote_handler_cbk.callback.assert_not_called()

    @staticmethod
    def test_buttons_triggered(
            tg_update_f: tg_Update,
            tg_dispatcher: tg_Dispatcher,
            monkeypatch,
    ):
        monkeypatch.setattr(tg_update_f.callback_query, 'data', app.tg.ptb.config.PUBLIC_VOTE_CBK_S)
        tg_dispatcher.process_update(update=tg_update_f)
        app.tg.ptb.handlers_definition.accept_public_vote_handler_cbk.callback.assert_called_once()


class TestPersonalVoteCbkHandler:

    @staticmethod
    @pytest.mark.parametrize(
        argnames='cbk_data', argvalues=[
            *get_text_cases(texts=[app.tg.ptb.config.PERSONAL_VOTE_CBK_S], lower=False, ),
            *get_text_cases(texts=['foo', 'bar egg'], )
        ],)
    def test_buttons_not_triggered(
            tg_update_f: tg_Update,
            tg_dispatcher: tg_Dispatcher,
            cbk_data: str,
            monkeypatch,
    ):
        monkeypatch.setattr(tg_update_f.callback_query, 'data', cbk_data)
        tg_dispatcher.process_update(update=tg_update_f)
        app.tg.ptb.handlers_definition.accept_personal_vote_handler_cbk.callback.assert_not_called()

    @staticmethod
    def test_buttons_triggered(
            tg_update_f: tg_Update,
            tg_dispatcher: tg_Dispatcher,
            monkeypatch,
    ):
        monkeypatch.setattr(tg_update_f.callback_query, 'data', app.tg.ptb.config.PERSONAL_VOTE_CBK_S)
        tg_dispatcher.process_update(update=tg_update_f)
        app.tg.ptb.handlers_definition.accept_personal_vote_handler_cbk.callback.assert_called_once()

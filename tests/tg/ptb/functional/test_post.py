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

import app.config
import app.tg.ptb.config
import app.tg.ptb.handlers_definition

from tests.tg.ptb.functional.utils import set_command_to_tg_message, get_text_cases, cancel_body

if TYPE_CHECKING:
    # noinspection PyPackageRequirements
    from telegram import Location, PhotoSize


class TestCreatePublicPost:
    cls_to_test = app.tg.ptb.handlers_definition.PublicPostCH

    def test_entry_point(self, tg_update_f: tg_Update, tg_dispatcher: tg_Dispatcher, ):
        assert (tg_update_f.effective_chat.id, tg_update_f.effective_user.id,) not in self.cls_to_test.CH.conversations
        set_command_to_tg_message(
            tg_message=tg_update_f.effective_message,
            cmd_text=app.tg.ptb.config.CREATE_PUBLIC_POST_S,
        )
        tg_dispatcher.process_update(update=tg_update_f)
        self.cls_to_test.entry_point.callback.assert_called_once()

    # TODO different_post content, not only text
    def test_sample_handler(
            self,
            tg_update_f: tg_Update,
            tg_dispatcher: tg_Dispatcher,
            monkeypatch,
    ):
        self.cls_to_test.CH.conversations[(tg_update_f.effective_chat.id, tg_update_f.effective_user.id,)] = 0
        monkeypatch.setattr(tg_update_f.effective_message, 'text', 'foo')
        tg_dispatcher.process_update(update=tg_update_f)
        self.cls_to_test.sample_handler.callback.assert_called_once()

    @pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=[app.constants.Shared.Words.SEND]))
    def test_confirm_handler(
            self,
            tg_update_f: tg_Update,
            tg_dispatcher: tg_Dispatcher,
            text: str,
            monkeypatch,
    ):
        self.cls_to_test.CH.conversations[(tg_update_f.effective_chat.id, tg_update_f.effective_user.id,)] = 1
        monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
        tg_dispatcher.process_update(update=tg_update_f)
        self.cls_to_test.confirm_handler.callback.assert_called_once()
        self.cls_to_test.confirm_handler.callback.reset_mock()

    def test_cancel(
            self,
            tg_update_f: tg_Update,
            tg_dispatcher: tg_Dispatcher,
            monkeypatch,
    ):
        cancel_body(
            update=tg_update_f,
            dispatcher=tg_dispatcher,
            ch=self.cls_to_test.CH,
            callback=self.cls_to_test.cancel.callback,
            monkeypatch=monkeypatch,
        )


class TestCreatePersonalPost:

    class AttrsForInnerClses:
        cls_to_test = app.tg.ptb.handlers_definition.PersonalPostCH

    cls_to_test = AttrsForInnerClses.cls_to_test

    def test_entry_point(self, tg_update_f: tg_Update, tg_dispatcher: tg_Dispatcher, ):
        assert (tg_update_f.effective_chat.id, tg_update_f.effective_user.id,) not in self.cls_to_test.CH.conversations
        set_command_to_tg_message(
            tg_message=tg_update_f.effective_message,
            cmd_text=app.tg.ptb.config.CREATE_PERSONAL_POST_S,
        )
        tg_dispatcher.process_update(update=tg_update_f)
        self.cls_to_test.entry_point.callback.assert_called_once()
        key = (tg_update_f.effective_chat.id, tg_update_f.effective_user.id,)
        assert self.cls_to_test.CH.conversations[key] == self.cls_to_test.entry_point.callback()

    class TestEntryPointHandler(AttrsForInnerClses, ):
        """entry_point_handler"""

        def body(self, tg_dispatcher: tg_Dispatcher, tg_update_f: tg_Update, ):
            self.cls_to_test.CH.conversations[(tg_update_f.effective_chat.id, tg_update_f.effective_user.id,)] = 0
            tg_dispatcher.process_update(update=tg_update_f)
            self.cls_to_test.entry_point_handler.callback.assert_called_once()
            key = (tg_update_f.effective_chat.id, tg_update_f.effective_user.id,)
            assert self.cls_to_test.CH.conversations[key] == self.cls_to_test.entry_point_handler.callback()
            self.cls_to_test.entry_point_handler.callback.reset_mock()

        def test_location(
                self,
                tg_update_f: tg_Update,
                tg_dispatcher: tg_Dispatcher,
                tg_location: Location,
        ):
            tg_update_f.effective_message.location = tg_location
            self.body(tg_dispatcher=tg_dispatcher, tg_update_f=tg_update_f, )

        def test_photo(
                self,
                tg_update_f: tg_Update,
                tg_dispatcher: tg_Dispatcher,
                tg_ptb_photo_s: PhotoSize,
        ):
            tg_update_f.effective_message.photo = tg_ptb_photo_s
            self.body(tg_dispatcher=tg_dispatcher, tg_update_f=tg_update_f, )

        @pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=['foo']))
        def test_text(self, tg_update_f: tg_Update, tg_dispatcher: tg_Dispatcher, text: str, ):
            """entry_point"""
            self.cls_to_test.CH.conversations[(tg_update_f.effective_chat.id, tg_update_f.effective_user.id,)] = 0
            tg_update_f.effective_message.text = text

    @pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=['foo']))
    def test_text(self, tg_update_f: tg_Update, tg_dispatcher: tg_Dispatcher, text: str, ):
        self.cls_to_test.CH.conversations[(tg_update_f.effective_chat.id, tg_update_f.effective_user.id,)] = 1
        tg_update_f.effective_message.text = text
        tg_dispatcher.process_update(update=tg_update_f)
        self.cls_to_test.sample_handler.callback.assert_called_once()
        key = (tg_update_f.effective_chat.id, tg_update_f.effective_user.id,)
        assert self.cls_to_test.CH.conversations[key] == self.cls_to_test.sample_handler.callback()
        self.cls_to_test.sample_handler.callback.reset_mock()

    @pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=['foo']))
    def test_collection_handler(self, tg_update_f: tg_Update, tg_dispatcher: tg_Dispatcher, text: str, ):
        self.cls_to_test.CH.conversations[(tg_update_f.effective_chat.id, tg_update_f.effective_user.id,)] = 2
        tg_update_f.effective_message.text = text
        tg_dispatcher.process_update(update=tg_update_f)
        self.cls_to_test.collections_handler.callback.assert_called_once()
        key = (tg_update_f.effective_chat.id, tg_update_f.effective_user.id,)
        assert self.cls_to_test.CH.conversations[key] == self.cls_to_test.collections_handler.callback()
        self.cls_to_test.collections_handler.callback.reset_mock()

    @pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=[app.constants.Shared.Words.SEND]))
    def test_confirm_handler(self, tg_update_f: tg_Update, tg_dispatcher: tg_Dispatcher, text: str, ):
        # The same with "TestCreatePublicPost.post_confirm_handler"
        self.cls_to_test.CH.conversations[(tg_update_f.effective_chat.id, tg_update_f.effective_user.id,)] = 3
        tg_update_f.effective_message.text = text
        tg_dispatcher.process_update(update=tg_update_f)
        self.cls_to_test.confirm_handler.callback.assert_called_once()
        key = (tg_update_f.effective_chat.id, tg_update_f.effective_user.id,)
        assert self.cls_to_test.CH.conversations[key] == self.cls_to_test.confirm_handler.callback()
        self.cls_to_test.confirm_handler.callback.reset_mock()

    def test_cancel(
            self,
            tg_update_f: tg_Update,
            tg_dispatcher: tg_Dispatcher,
            monkeypatch,
    ):
        cancel_body(
            update=tg_update_f,
            dispatcher=tg_dispatcher,
            ch=self.cls_to_test.CH,
            callback=self.cls_to_test.cancel.callback,
            monkeypatch=monkeypatch,
        )


class TestSharePersonalPosts:
    cls_to_test = app.tg.ptb.handlers_definition.SharePersonalPostsCh

    def test_entry_point(self, tg_update_f: tg_Update, tg_dispatcher: tg_Dispatcher, ):
        assert (tg_update_f.effective_chat.id, tg_update_f.effective_user.id,) not in self.cls_to_test.CH.conversations
        set_command_to_tg_message(
            tg_message=tg_update_f.effective_message,
            cmd_text=app.tg.ptb.config.SHARE_PERSONAL_POSTS_S,
        )
        tg_dispatcher.process_update(update=tg_update_f)
        self.cls_to_test.entry_point.callback.assert_called_once()
        key = (tg_update_f.effective_chat.id, tg_update_f.effective_user.id,)
        assert self.cls_to_test.CH.conversations[key] == self.cls_to_test.entry_point.callback()

    def test_recipient_handler(
            self,
            tg_update_f: tg_Update,
            tg_dispatcher: tg_Dispatcher,
            monkeypatch,
    ):
        self.cls_to_test.CH.conversations[tg_update_f.effective_chat.id, tg_update_f.effective_user.id] = 0
        monkeypatch.setattr(tg_update_f.effective_message, 'text', '1')
        tg_dispatcher.process_update(update=tg_update_f)
        self.cls_to_test.recipient_handler.callback.assert_called_once()
        key = (tg_update_f.effective_chat.id, tg_update_f.effective_user.id,)
        assert self.cls_to_test.CH.conversations[key] == self.cls_to_test.recipient_handler.callback()

    def test_cancel(
            self,
            tg_update_f: tg_Update,
            tg_dispatcher: tg_Dispatcher,
            monkeypatch,
    ):
        cancel_body(
            update=tg_update_f,
            dispatcher=tg_dispatcher,
            ch=self.cls_to_test.CH,
            callback=self.cls_to_test.cancel.callback,
            monkeypatch=monkeypatch,
        )


class TestRequestPersonalPosts:
    cls_to_test = app.tg.ptb.handlers_definition.RequestPersonalPostsCH

    def test_entry_point(self, tg_update_f: tg_Update, tg_dispatcher: tg_Dispatcher, ):
        assert (tg_update_f.effective_chat.id, tg_update_f.effective_user.id,) not in self.cls_to_test.CH.conversations
        set_command_to_tg_message(
            tg_message=tg_update_f.effective_message,
            cmd_text=app.tg.ptb.config.REQUEST_PERSONAL_POSTS_S
        )
        tg_dispatcher.process_update(update=tg_update_f)
        self.cls_to_test.entry_point.callback.assert_called_once()
        key = (tg_update_f.effective_chat.id, tg_update_f.effective_user.id,)
        assert self.cls_to_test.CH.conversations[key] == self.cls_to_test.entry_point.callback()

    @pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=['1', '2', 'sdfs%W']))  # users ids
    def test_recipient_handler(
            self,
            tg_update_f: tg_Update,
            tg_dispatcher: tg_Dispatcher,
            text: str,
            monkeypatch,
    ):
        self.cls_to_test.CH.conversations[(tg_update_f.effective_chat.id, tg_update_f.effective_user.id,)] = 0
        monkeypatch.setattr(tg_update_f.effective_message, 'text', text)
        tg_dispatcher.process_update(update=tg_update_f)
        self.cls_to_test.recipient_handler.callback.assert_called_once()
        key = (tg_update_f.effective_chat.id, tg_update_f.effective_user.id,)
        assert self.cls_to_test.CH.conversations[key] == self.cls_to_test.recipient_handler.callback()
        self.cls_to_test.recipient_handler.callback.reset_mock()

    def test_cancel(
            self,
            tg_update_f: tg_Update,
            tg_dispatcher: tg_Dispatcher,
            monkeypatch,
    ):
        cancel_body(
            update=tg_update_f,
            dispatcher=tg_dispatcher,
            ch=self.cls_to_test.CH,
            callback=self.cls_to_test.cancel.callback,
            monkeypatch=monkeypatch,
        )


def test_share_personal_post_cbk(tg_update_f: tg_Update, tg_dispatcher: tg_Dispatcher, ):
    tg_update_f.callback_query.data = app.tg.ptb.config.ACCEPT_PERSONAL_POSTS_CBK_S
    tg_dispatcher.process_update(update=tg_update_f)
    app.tg.ptb.handlers_definition.share_personal_posts_handler_cbk.callback.assert_called_once()
    app.tg.ptb.handlers_definition.share_personal_posts_handler_cbk.callback.reset_mock()


def test_get_my_personal_posts_cmd(tg_update_f: tg_Update, tg_dispatcher: tg_Dispatcher, ):
    set_command_to_tg_message(tg_message=tg_update_f.message, cmd_text=app.tg.ptb.config.GET_MY_PERSONAL_POSTS_S)
    tg_dispatcher.process_update(update=tg_update_f)
    app.tg.ptb.handlers_definition.get_my_personal_posts_handler_cmd.callback.assert_called_once()


@pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=[app.tg.ptb.config.GET_PUBLIC_POST_S], ))
def test_get_public_post_cmd(
        tg_update_f: tg_Update,
        tg_dispatcher: tg_Dispatcher,
        text: str,
):
    set_command_to_tg_message(tg_message=tg_update_f.message, cmd_text=text)
    tg_dispatcher.process_update(update=tg_update_f)
    app.tg.ptb.handlers_definition.get_public_post_handler_cmd.callback.assert_called_once()
    app.tg.ptb.handlers_definition.get_public_post_handler_cmd.callback.reset_mock()


class TestGetPendingPublicPostsCmd:
    @staticmethod
    def test_admin_restriction_success(
            tg_update_f: tg_Update,
            tg_dispatcher: tg_Dispatcher,
    ):
        set_command_to_tg_message(tg_message=tg_update_f.message, cmd_text=app.tg.ptb.config.CREATE_PUBLIC_POST_S)
        tg_dispatcher.process_update(update=tg_update_f)
        app.tg.ptb.handlers_definition.get_pending_public_posts_handler_cmd.callback.assert_not_called()

    @staticmethod
    def test_success(
            tg_update_f: tg_Update,
            tg_dispatcher: tg_Dispatcher,
            monkeypatch,
    ):
        monkeypatch.setattr(tg_update_f.effective_user, 'id', app.config.MAIN_ADMIN)
        set_command_to_tg_message(tg_message=tg_update_f.message, cmd_text=app.tg.ptb.config.GET_PENDING_POSTS_S)
        tg_dispatcher.process_update(update=tg_update_f)
        app.tg.ptb.handlers_definition.get_pending_public_posts_handler_cmd.callback.assert_called_once()


class TestPublicPostMassSendingHandlerCmd:
    @staticmethod
    def test_admin_restriction_success(
            tg_update_f: tg_Update,
            tg_dispatcher: tg_Dispatcher,
    ):
        set_command_to_tg_message(tg_message=tg_update_f.message, cmd_text=app.tg.ptb.config.SEND_S)
        tg_dispatcher.process_update(update=tg_update_f)
        app.tg.ptb.handlers_definition.public_post_mass_sending_handler_cmd.callback.assert_not_called()

    @staticmethod
    @pytest.mark.parametrize(argnames='text', argvalues=get_text_cases(texts=[app.tg.ptb.config.SEND_S], ))
    def test_success(
            tg_update_f: tg_Update,
            tg_dispatcher: tg_Dispatcher,
            text: str,
            monkeypatch,
    ):
        monkeypatch.setattr(tg_update_f.effective_user, 'id', app.config.MAIN_ADMIN)
        set_command_to_tg_message(tg_message=tg_update_f.message, cmd_text=text)
        tg_dispatcher.process_update(update=tg_update_f)
        app.tg.ptb.handlers_definition.public_post_mass_sending_handler_cmd.callback.assert_called_once()
        app.tg.ptb.handlers_definition.public_post_mass_sending_handler_cmd.callback.reset_mock()


@pytest.mark.parametrize(argnames='flag', argvalues=['0', '1'])
def test_request_personal_post_cbk(tg_update_f: tg_Update, tg_dispatcher: tg_Dispatcher, flag: str, ):
    tg_update_f.callback_query.data = (
        f'{app.tg.ptb.config.REQUEST_PERSONAL_POSTS_CBK_S} '
        f'{tg_update_f.effective_user.id} {flag}'
    )
    tg_dispatcher.process_update(update=tg_update_f)
    app.tg.ptb.handlers_definition.request_personal_post_handler_cbk.callback.assert_called_once()
    app.tg.ptb.handlers_definition.request_personal_post_handler_cbk.callback.reset_mock()


def test_update_public_post_status_cbk(
        tg_update_f: tg_Update,
        tg_dispatcher: tg_Dispatcher,
        monkeypatch,
):
    """update_post_status"""
    monkeypatch.setattr(tg_update_f.callback_query, 'data', app.tg.ptb.config.UPDATE_PUBLIC_POST_STATUS_CBK_S)
    tg_dispatcher.process_update(update=tg_update_f)
    app.tg.ptb.handlers_definition.update_public_post_status_handler_cbk.callback.assert_called_once()

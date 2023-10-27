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

from unittest.mock import patch
from typing import TYPE_CHECKING, Any as typing_Any

import pytest
# noinspection PyPackageRequirements
from telegram import Update as tg_Update
# noinspection PyPackageRequirements
from telegram.error import Unauthorized, BadRequest

from app.tg.ptb import services, handlers, actions, constants
from app.tg.ptb.classes.collections import Collection

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from app import models


class TestSharePersonalCollections:
    """CreatePersonalPost"""

    class AttrsForInnerClses:
        class_to_test = handlers.collections.SharePersonalCollections

    class_to_test = AttrsForInnerClses.class_to_test

    def test_entry_point_no_collections(self, mock_context: MagicMock, monkeypatch):
        monkeypatch.setattr(mock_context.user_data.current_user.get_collections, 'return_value', [])
        # Execution
        result = self.class_to_test.entry_point(_=typing_Any, context=mock_context, )
        # Checks
        mock_context.user_data.view.collections.no_collections.assert_called_once_with()
        assert len(mock_context.user_data.view.mock_calls) == 1
        assert result == -1

    def test_entry_point(self, mock_context: MagicMock, ):
        # Execution
        result = self.class_to_test.entry_point(_=typing_Any, context=mock_context, )
        # Checks
        mock_context.user_data.current_user.get_collections.assert_called_once_with(cache=True, )
        mock_context.user_data.view.collections.show_collections.assert_called_once_with(
            collections=mock_context.user_data.current_user.get_collections.return_value,
            text=constants.Collections.ASK_TO_SHARE,
        )
        mock_context.user_data.view.notify_ready_keyword.assert_called_once_with()
        assert len(mock_context.user_data.view.mock_calls) == 2
        assert result == 0

    def test_mark_to_share_cbk_handler(self, tg_update_f: tg_Update, mock_context: MagicMock, monkeypatch):
        """mark_show_cbk_handler"""
        collection_id = 1
        monkeypatch.setattr(tg_update_f.callback_query, 'data', f'_  {collection_id}')
        # Before 
        assert mock_context.user_data.tmp_data.collections_id_to_share == set()
        # Execution
        result = self.class_to_test.mark_to_share_cbk_handler(update=tg_update_f, context=mock_context, )
        # Checks
        assert mock_context.user_data.tmp_data.collections_id_to_share == {collection_id, }
        assert result is None

    def test_continue_handler_incorrect(
            self,
            tg_update_f: tg_Update,
            mock_context: MagicMock,
            monkeypatch,
    ):
        """continue_handler"""
        monkeypatch.setattr(tg_update_f.effective_message, 'text', 'foo')
        # Execution
        result = self.class_to_test.continue_handler(update=tg_update_f, context=mock_context, )
        # Checks
        mock_context.user_data.view.warn.incorrect_finish.assert_called_once_with()
        assert len(mock_context.user_data.view.mock_calls) == 1
        assert result is None

    def test_continue_handler_collections_not_chosen(
            self,
            tg_update_f: tg_Update,
            mock_context: MagicMock,
            monkeypatch,
    ):
        """continue_handler"""
        monkeypatch.setattr(tg_update_f.effective_message, 'text', constants.Shared.Words.FINISH)
        mock_context.user_data.tmp_data.collections_id_to_share = set()
        # Execution
        result = self.class_to_test.continue_handler(update=tg_update_f, context=mock_context, )
        # Checks
        mock_context.user_data.view.collections.collections_to_share_not_chosen.assert_called_once_with()
        assert len(mock_context.user_data.view.mock_calls) == 1
        assert result is None

    def test_continue_handler(
            self,
            tg_update_f: tg_Update,
            mock_context: MagicMock,
            monkeypatch,
    ):
        """continue_handler"""
        monkeypatch.setattr(tg_update_f.effective_message, 'text', constants.Shared.Words.FINISH)
        monkeypatch.setattr(mock_context.user_data.tmp_data, 'collections_id_to_share', {1, 2, 3})
        # Execution
        result = self.class_to_test.continue_handler(update=tg_update_f, context=mock_context, )
        # Checks
        mock_context.user_data.view.collections.ask_who_to_share.assert_called_once_with()
        assert len(mock_context.user_data.view.mock_calls) == 1
        assert result == 1

    class TestCheckRecipientHandler(AttrsForInnerClses):

        def test_incorrect_user(self, tg_update_f: tg_Update, mock_context: MagicMock, ):
            with patch.object(
                    actions,
                    'accept_user_handler',
                    return_value=None,
            ) as mock_accept_user_handler:
                result = self.class_to_test.recipient_handler(update=tg_update_f, context=mock_context, )
            mock_accept_user_handler.assert_called_once_with(update=tg_update_f, context=mock_context, )
            mock_context.user_data.view.collections.ask_accept_collections.assert_not_called()
            assert result is None

        @pytest.mark.parametrize(argnames='error', argvalues=(BadRequest, Unauthorized,))
        def test_recipient_not_found(self, tg_update_f: tg_Update, mock_context: MagicMock, error: type, monkeypatch):
            monkeypatch.setattr(
                mock_context.user_data.view.collections.ask_accept_collections,
                'side_effect',
                error('foo'),
            )
            with patch.object(actions, 'accept_user_handler', autospec=True) as mock_accept_user_handler:
                result = self.class_to_test.recipient_handler(update=tg_update_f, context=mock_context, )
            mock_accept_user_handler.assert_called_once_with(update=tg_update_f, context=mock_context, )
            mock_context.user_data.view.collections.ask_accept_collections.assert_called_once_with(
                recipient_tg_user_id=mock_accept_user_handler.return_value,
                collections_ids=mock_context.user_data.tmp_data.collections_id_to_share,
            )
            mock_context.user_data.view.user_not_found.assert_called_once_with()
            assert len(mock_context.mock_calls) == 2
            assert result is None

        def test_success(self, tg_update_f: tg_Update, mock_context: MagicMock, ):
            with patch.object(actions, 'accept_user_handler', autospec=True) as mock_accept_user_handler:
                result = self.class_to_test.recipient_handler(update=tg_update_f, context=mock_context, )
            mock_accept_user_handler.assert_called_once_with(update=tg_update_f, context=mock_context, )
            mock_context.user_data.view.collections.ask_accept_collections.assert_called_once_with(
                recipient_tg_user_id=mock_accept_user_handler.return_value,
                collections_ids=mock_context.user_data.tmp_data.collections_id_to_share,
            )
            mock_context.user_data.view.posts.say_user_got_share_proposal.assert_called_once_with(
                recipient_tg_user_id=mock_accept_user_handler.return_value,
            )
            assert len(mock_context.mock_calls) == 2
            assert result == -1

    class TestAcceptCollectionsCbk(AttrsForInnerClses):
        def test_declined(
                self,
                mock_context: MagicMock,
                tg_update_f: tg_Update,
                mock_ptb_bot: MagicMock,
                monkeypatch,
        ):
            """accept_collections_cbk"""
            monkeypatch.setattr(tg_update_f.callback_query, 'data', f'_ 1 0')  # user_id, flag
            # Execution
            self.class_to_test.recipient_decision_cbk_handler(update=tg_update_f, context=mock_context, )
            # Checks
            mock_context.user_data.view.collections.recipient_declined_share_proposal.assert_called_once_with(
                sender_tg_user_id=1,
            )
            mock_ptb_bot.answer_callback_query.assert_called_once()

        def test_collections_not_exists(
                self,
                mock_context: MagicMock,
                tg_update_f: tg_Update,
                mock_ptb_bot: MagicMock,
                monkeypatch,
        ):
            """accept_collections_cbk"""
            monkeypatch.setattr(tg_update_f.callback_query, 'data', f'_ 1 2 3')
            # Execution
            with patch.object(services.Collection, 'get_by_ids', autospec=True, return_value=[], ) as mock_get_by_ids:
                self.class_to_test.recipient_decision_cbk_handler(update=tg_update_f, context=mock_context, )
            mock_get_by_ids.assert_called_once_with(ids=[3, ], user=mock_context.user_data.current_user, )
            mock_ptb_bot.answer_callback_query.assert_called_once()

        def test_accepted(
                self,
                mock_context: MagicMock,
                tg_update_f: tg_Update,
                collection: models.collections.Collection,
                mock_ptb_bot: MagicMock,
                monkeypatch,
        ):
            """accept_collections_cbk_handler"""
            monkeypatch.setattr(tg_update_f.callback_query, 'data', f'_ 1 2 3')
            monkeypatch.setattr(mock_context.user_data.tmp_data, 'collections_id_to_share', {1, 2, 3})
            # Execution
            with patch.object(
                    services.Collection,
                    'get_by_ids',
                    autospec=True,
                    return_value=[collection],
            ) as mock_get_by_ids:
                self.class_to_test.recipient_decision_cbk_handler(update=tg_update_f, context=mock_context, )
            # Checks
            mock_get_by_ids.assert_called_once_with(ids=[3, ], user=mock_context.user_data.current_user, )
            mock_context.user_data.view.collections.show_collections_to_recipient.assert_called_once_with(
                sender_tg_user_id=tg_update_f.effective_user.id,
                collections=[collection],
            )
            mock_ptb_bot.answer_callback_query.assert_called_once()

    def test_show_collection_posts_to_recipient_cbk_handler(
            self,
            mock_context: MagicMock,
            tg_update_f: tg_Update,
            mock_ptb_bot: MagicMock,
    ):
        with (
            patch.object(
                Collection.Keyboards.ShowPostsForRecipient,
                'extract_cbk_data',
                autospec=True,
            ) as mock_extract_cbk_data,
            patch.object(Collection, 'get_posts', autospec=True, ) as mock_get_posts,
            patch.object(services.Post, 'prepare_for_send', autospec=True, ) as mock_prepare_for_send,
        ):
            mock_extract_cbk_data.return_value = [1, 2, ]
            self.class_to_test.show_collection_posts_to_recipient_cbk_handler(
                update=tg_update_f,
                context=mock_context,
            )
        mock_extract_cbk_data.assert_called_once_with(
            cbk_data=tg_update_f.callback_query.data,
            user=mock_context.user_data.current_user,
        )
        mock_get_posts.assert_called_once_with(
            collection_id=2,
            connection=mock_context.user_data.current_user.connection,
        )
        mock_prepare_for_send.assert_called_once_with(
            posts=mock_get_posts.return_value,
            clicker=mock_context.user_data.current_user,
            opposite=1,
        )
        mock_context.user_data.view.collections.show_collection_posts.assert_called_once_with(
            posts=mock_prepare_for_send.return_value,
        )
        mock_ptb_bot.answer_callback_query.assert_called_once()

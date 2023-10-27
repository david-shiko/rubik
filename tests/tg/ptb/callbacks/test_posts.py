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

from custom_ptb.callback_context import CustomCallbackContext

import app.services

from app.tg.ptb.views import View
import app.tg.ptb.config
import app.tg.ptb.utils
import app.tg.ptb.classes.posts
import app.tg.ptb.handlers.posts

import app.tg.ptb.forms.post
import app.tg.ptb.services

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from app.tg.ptb.classes.collections import Collection


class TestCreatePublicPost:

    @staticmethod
    def test_create_public_post(mock_context: MagicMock, monkeypatch, ):
        monkeypatch.setattr(mock_context.user_data.current_user, 'is_registered', True)
        # Before 
        mock_context.user_data.forms.post = None
        # Execution
        result = app.tg.ptb.handlers.posts.CreatePublicPost.entry_point(_=typing_Any, context=mock_context, )
        # Checks
        mock_context.user_data.view.posts.say_public_post_hello.assert_called_once_with()

        assert result == 0

    @staticmethod
    def test_sample_handler(
            mock_context: MagicMock,
            tg_update_f: tg_Update,
            mock_ptb_public_post_form: MagicMock,
    ):
        with patch.object(
                app.tg.ptb.forms.post,
                'PublicPost',
                autospec=True,
                return_value=mock_ptb_public_post_form,
        ) as mock_post_form_cls:
            result = app.tg.ptb.handlers.posts.CreatePublicPost.sample_handler(
                update=tg_update_f,
                context=mock_context,
            )
        mock_post_form_cls.assert_called_once_with(author=mock_context.user_data.current_user, message_id=1, )
        assert mock_context.user_data.forms.post == mock_post_form_cls.return_value
        mock_context.user_data.view.posts.here_post_preview.assert_called_once_with()
        mock_context.user_data.view.posts.show_post.assert_called_once_with(
            post=mock_context.user_data.forms.post,
        )

        assert result == 1

    @staticmethod
    def test_post_confirm_handler_incorrect(mock_context: MagicMock, tg_update_f: tg_Update, monkeypatch, ):
        monkeypatch.setattr(tg_update_f.effective_message, 'text', 'foo')
        # Execution
        result = app.tg.ptb.handlers.posts.CreatePublicPost.confirm_handler(update=tg_update_f, context=mock_context, )
        # Checks
        mock_context.user_data.view.warn.incorrect_send.assert_called_once_with()

        assert result is None

    @staticmethod
    def test_confirm_handler(mock_context: MagicMock, tg_update_f: tg_Update, monkeypatch, ):
        """confirm_handler"""
        monkeypatch.setattr(tg_update_f.effective_message, 'text', app.constants.Shared.Words.SEND)
        mock_post = mock_context.user_data.forms.post  # need to save the val of a real mock before setting to none it
        with patch.object(app.services.System, 'set_bots_votes_to_post', autospec=True, ) as mock_set_bot_votes:
            result = app.tg.ptb.handlers.posts.CreatePublicPost.confirm_handler(
                update=tg_update_f,
                context=mock_context,
            )
        assert result == -1
        mock_context.user_data.view.posts.say_success_post.assert_called_once_with()
        mock_post.create.assert_called_once_with()
        mock_set_bot_votes.assert_called_once_with(post=mock_post.create.return_value, )
        assert mock_context.user_data.forms.post is None  # mock_context.user_data.forms.post now refers to None


class TestCreatePersonalPost:
    """CreatePersonalPost"""

    @staticmethod
    def test_entry_point(mock_context: MagicMock, ):
        # Before
        mock_context.user_data.forms.post = None
        # Execution
        result = app.tg.ptb.handlers.posts.CreatePersonalPost.entry_point(_=typing_Any, context=mock_context, )
        # Checks
        assert result == 0
        mock_context.user_data.view.posts.say_personal_post_hello.assert_called_once_with()
        # Mock call always the same

    @staticmethod
    def test_entry_point_handler(
            mock_context: MagicMock,
            tg_update_f: tg_Update,
            mock_ptb_personal_post_form: MagicMock,
    ):
        # Execution
        with patch.object(
                app.tg.ptb.forms.post,
                'PersonalPost',
                autospec=True,
                return_value=mock_ptb_personal_post_form,
        ) as mock_post_form_cls:
            result = app.tg.ptb.handlers.posts.CreatePersonalPost.entry_point_handler(
                update=tg_update_f,
                context=mock_context,
            )
        # Checks
        assert result == 1
        mock_post_form_cls.assert_called_once_with(author=mock_context.user_data.current_user, message_id=1, )
        assert mock_context.user_data.forms.post == mock_post_form_cls.return_value
        mock_context.user_data.view.posts.show_post.assert_called_once_with(
            post=mock_context.user_data.forms.post,
        )

    @staticmethod
    def test_sample_handler_incorrect(mock_context: MagicMock, tg_update_f: tg_Update, monkeypatch, ):
        """sample_handler"""
        monkeypatch.setattr(tg_update_f.effective_message, 'text', 'foo', )
        # Execution
        result = app.tg.ptb.handlers.posts.CreatePersonalPost.sample_handler(update=tg_update_f, context=mock_context, )
        # Checks
        assert result is None
        mock_context.user_data.view.warn.incorrect_continue.assert_called_with(
            keyword=app.tg.ptb.handlers.posts.CreatePersonalPost.READY_KEYWORD
        )

    class TestSampleHandler:

        @staticmethod
        def body(mock_context: MagicMock, tg_update_f: tg_Update, monkeypatch, ):
            assert mock_context.user_data.current_user.collections == []
            monkeypatch.setattr(
                tg_update_f.effective_message,
                'text',
                app.tg.ptb.handlers.posts.CreatePersonalPost.READY_KEYWORD,
            )
            # Execution
            result = app.tg.ptb.handlers.posts.CreatePersonalPost.sample_handler(
                update=tg_update_f, context=mock_context, )
            # Checks
            assert result == 2
            mock_context.user_data.current_user.get_collections.assert_called_once_with()

        def test_user_collections_from_db_exists(
                self,
                mock_context: MagicMock,
                tg_update_f: tg_Update,
                ptb_collection_s: Collection,
                monkeypatch,
        ):
            """sample_handler"""
            # Before
            assert mock_context.user_data.current_user.collections == []
            monkeypatch.setattr(
                mock_context.user_data.current_user.get_collections, 'return_value', [ptb_collection_s], )
            # Execution
            self.body(mock_context=mock_context, tg_update_f=tg_update_f, monkeypatch=monkeypatch, )
            mock_context.user_data.view.collections.ask_collection_for_post.assert_called_once_with(
                collection_names={
                    collection.name for collection in mock_context.user_data.current_user.get_collections.return_value
                }, )

        def test_user_collections_from_db_not_exists(
                self,
                mock_context: MagicMock,
                tg_update_f: tg_Update,
                ptb_collection_s: Collection,
                monkeypatch,
        ):
            """sample_handler"""

            # Execution
            self.body(mock_context=mock_context, tg_update_f=tg_update_f, monkeypatch=monkeypatch, )
            mock_context.user_data.view.collections.ask_collection_for_post.assert_called_once_with(
                collection_names=mock_context.user_data.forms.post.collection_names,
            )

    @staticmethod
    def test_collections_handler_skip(mock_context: MagicMock, tg_update_f: tg_Update, monkeypatch, ):
        """collections_handler"""
        monkeypatch.setattr(tg_update_f.effective_message, 'text', app.constants.Shared.Words.SKIP)
        # Execution
        result = app.tg.ptb.handlers.posts.CreatePersonalPost.collections_handler(
            update=tg_update_f,
            context=mock_context,
        )
        # Checks
        assert result == 3
        mock_context.user_data.view.collections.show_chosen_collections_for_post.assert_called_once_with(
            collection_names=mock_context.user_data.forms.post.collection_names,
        )

    @staticmethod
    def test_collections_handler(mock_context: MagicMock, tg_update_f: tg_Update, monkeypatch, ):
        """collections_handler"""
        monkeypatch.setattr(tg_update_f.effective_message, 'text', '1, ewe, werwe', )
        # Execution
        result = app.tg.ptb.handlers.posts.CreatePersonalPost.collections_handler(
            update=tg_update_f,
            context=mock_context,
        )
        # Checks
        mock_context.user_data.forms.post.handle_collection_names.assert_called_once_with(text='1, ewe, werwe', )
        assert result == 3
        mock_context.user_data.view.collections.show_chosen_collections_for_post.assert_called_once_with(
            collection_names=mock_context.user_data.forms.post.collection_names,
        )

    class TestConfirmHandler:
        """test_confirm_handler"""

        @staticmethod
        def test_incorrect(mock_context: MagicMock, tg_update_f: tg_Update, monkeypatch, ):
            """confirm_handler"""
            monkeypatch.setattr(tg_update_f.effective_message, 'text', 'foo')
            # Execution
            result = app.tg.ptb.handlers.posts.CreatePersonalPost.confirm_handler(
                update=tg_update_f,
                context=mock_context, )
            # Checks
            assert result is None
            mock_context.user_data.view.warn.incorrect_finish.assert_called_once_with()

        @staticmethod
        def test_success(mock_context: MagicMock, tg_update_f: tg_Update, monkeypatch, ):
            """confirm_handler"""
            monkeypatch.setattr(tg_update_f.effective_message, 'text', app.constants.Shared.Words.FINISH, )
            # Create alias cuz forms.post will be None after test but alias preserves ref to post form
            post_form = mock_context.user_data.forms.post
            # Execution
            result = app.tg.ptb.handlers.posts.CreatePersonalPost.confirm_handler(
                update=tg_update_f,
                context=mock_context,
            )
            assert result == -1
            mock_context.user_data.view.posts.say_success_post.assert_called_once_with()
            post_form.create.assert_called_once_with()


class TestSharePersonalPosts:
    class_to_test = app.tg.ptb.handlers.posts.SharePersonalPosts

    def test_entry_point_no_posts(self, mock_context: MagicMock, ):
        with patch.object(
                mock_context.user_data.current_user,
                'get_personal_posts',
                return_value=[],
        ) as mock_get_personal_posts:
            result = self.class_to_test.entry_point(_=typing_Any, context=mock_context, )
        mock_get_personal_posts.assert_called_once_with()
        mock_context.user_data.view.posts.no_personal_posts.assert_called_once_with()

        assert result == -1

    def test_entry_point(self, mock_context: MagicMock, monkeypatch, ):
        result = self.class_to_test.entry_point(_=typing_Any, context=mock_context, )
        mock_context.user_data.current_user.get_personal_posts.assert_called_once_with()
        mock_context.user_data.view.posts.ask_who_to_share_personal_posts.assert_called_once_with()

        assert result == 0

    class TestRecipientHandler:
        """recipient_handler_incorrect"""
        class_to_test = app.tg.ptb.handlers.posts.SharePersonalPosts

        def test_incorrect(
                self,
                mock_context: CustomCallbackContext,
                tg_update_f: tg_Update,
                monkeypatch,
        ):
            monkeypatch.setattr(tg_update_f.effective_message, 'text', 'foo')
            with patch.object(app.tg.ptb.utils, 'accept_user', autospec=True, return_value=None, ) as mock_accept_user:
                result = self.class_to_test.recipient_handler(update=tg_update_f, context=mock_context, )
            mock_accept_user.assert_called_once_with(message=tg_update_f.effective_message)
            mock_context.user_data.view.warn.incorrect_user.assert_called_once_with()

            assert result is None

        @pytest.mark.parametrize(argnames='error', argvalues=(BadRequest, Unauthorized,), )
        def test_user_not_found(
                self,
                mock_context: MagicMock,
                tg_update_f: tg_Update,
                error: type,
                monkeypatch,
        ):
            monkeypatch.setattr(
                mock_context.user_data.view.posts.ask_accept_personal_posts,
                'side_effect',
                error('foo'),
            )
            with patch.object(app.tg.ptb.utils, 'accept_user', autospec=True, ) as mock_accept_user:
                result = self.class_to_test.recipient_handler(update=tg_update_f, context=mock_context, )
            mock_accept_user.assert_called_once_with(message=tg_update_f.effective_message)
            mock_context.user_data.view.posts.ask_accept_personal_posts.assert_called_once_with(
                recipient_tg_user_id=mock_accept_user.return_value,
            )
            mock_context.user_data.view.user_not_found.assert_called_once_with()

            assert result is None

        # Both contact and text are the same test
        def test_success(
                self,
                mock_context: MagicMock,
                tg_update_f: tg_Update,
                monkeypatch,
        ):
            with patch.object(app.tg.ptb.utils, 'accept_user', autospec=True, return_value='1') as mock_accept_user:
                result = self.class_to_test.recipient_handler(update=tg_update_f, context=mock_context, )
            mock_accept_user.assert_called_once_with(message=tg_update_f.effective_message)
            mock_context.user_data.view.posts.ask_accept_personal_posts.assert_called_once_with(
                recipient_tg_user_id=mock_accept_user.return_value,
            )
            mock_context.user_data.view.posts.say_user_got_share_proposal.assert_called_once_with(
                recipient_tg_user_id=mock_accept_user.return_value,
            )
            # Need 2 calls for logic
            assert result == -1


class TestRequestPersonalPosts:
    cls_to_test = app.tg.ptb.handlers.posts.RequestPersonalPosts

    def test_entry_point(self, mock_context: MagicMock, monkeypatch):
        # Execution
        result = self.cls_to_test.entry_point(_=typing_Any, context=mock_context, )
        # Checks
        mock_context.user_data.view.posts.ask_who_to_request_personal_posts.assert_called_once_with()

        assert result == 0

    class TestRecipientHandler:
        """recipient_handler_incorrect"""
        cls_to_test = app.tg.ptb.handlers.posts.RequestPersonalPosts

        def test_incorrect(
                self,
                tg_update_f: tg_Update,
                mock_context: MagicMock,
        ):
            """continue_handler"""
            with patch.object(app.tg.ptb.utils, 'accept_user', autospec=True, return_value=None, ) as mock_accept_user:
                result = self.cls_to_test.recipient_handler(update=tg_update_f, context=mock_context, )
            # Checks
            mock_accept_user.assert_called_once_with(message=tg_update_f.effective_message)
            mock_context.user_data.view.warn.incorrect_user.assert_called_once_with()

            assert result is None

        @pytest.mark.parametrize(argnames='error', argvalues=(BadRequest, Unauthorized,), )
        def test_not_found(
                self,
                tg_update_f: tg_Update,
                mock_context: MagicMock,
                error: type,
                monkeypatch,
        ):
            """continue_handler"""
            monkeypatch.setattr(
                mock_context.user_data.view.posts.ask_permission_to_share_personal_posts,
                'side_effect',
                error('foo'),
            )
            with patch.object(app.tg.ptb.utils, 'accept_user', autospec=True, ) as mock_accept_user:
                result = self.cls_to_test.recipient_handler(update=tg_update_f, context=mock_context, )
            # Checks
            mock_accept_user.assert_called_once_with(message=tg_update_f.effective_message)
            mock_context.user_data.view.posts.ask_permission_to_share_personal_posts.assert_called_once_with(
                recipient_tg_user_id=mock_accept_user.return_value,
            )
            mock_context.user_data.view.user_not_found.assert_called_once_with()

            assert result is None

        def test_success(
                self,
                tg_update_f: tg_Update,
                mock_context: MagicMock,
        ):
            """continue_handler"""
            with patch.object(app.tg.ptb.utils, 'accept_user', autospec=True, return_value='1', ) as mock_accept_user:
                result = self.cls_to_test.recipient_handler(update=tg_update_f, context=mock_context, )
            # Checks
            mock_accept_user.assert_called_once_with(message=tg_update_f.effective_message)
            mock_context.user_data.view.posts.ask_permission_to_share_personal_posts.assert_called_once_with(
                recipient_tg_user_id=mock_accept_user.return_value, )
            mock_context.user_data.view.posts.say_user_got_request_proposal.assert_called_once_with(
                recipient_tg_user_id=mock_accept_user.return_value,
            )

            assert result == -1


class TestGetMyCollections:
    @staticmethod
    def test_no_collections(mock_context: MagicMock, monkeypatch):
        monkeypatch.setattr(mock_context.user_data.current_user.get_collections, 'return_value', [])
        app.tg.ptb.handlers.posts.get_my_collections_handler_cmd(_=typing_Any, context=mock_context, )
        mock_context.user_data.current_user.get_collections.assert_called_once_with()
        mock_context.user_data.view.collections.no_collections.assert_called_once_with()

    @staticmethod
    def test_success(mock_context: MagicMock, ):
        app.tg.ptb.handlers.posts.get_my_collections_handler_cmd(_=typing_Any, context=mock_context, )
        mock_context.user_data.current_user.get_collections.assert_called_once_with()
        mock_context.user_data.view.collections.show_my_collections.assert_called_once_with(
            collections=mock_context.user_data.current_user.get_collections.return_value,
        )


class TestSharePersonalPostCbkHandler:

    @staticmethod
    def test_accept_button(
            tg_update_f: tg_Update,
            mock_context: MagicMock,
            mock_ptb_user: MagicMock,
            patched_ptb_personal_post: MagicMock,
            monkeypatch,
    ):
        tg_name = mock_context.user_data.current_user.tg_name
        patched_ptb_personal_post.extract_cbk_data.return_value = [mock_ptb_user, None, ]
        mock_posts_sender = patched_ptb_personal_post.extract_cbk_data.return_value[0]
        monkeypatch.setattr(mock_context.user_data.current_user, 'is_registered', True)
        monkeypatch.setattr(patched_ptb_personal_post.extract_cbk_data, 'return_value', [mock_posts_sender, True, ], )
        # Execution
        result = app.tg.ptb.handlers.posts.share_personal_posts_cbk_handler(update=tg_update_f, context=mock_context, )
        # Checks
        patched_ptb_personal_post.extract_cbk_data.assert_called_once_with(
            callback_data=tg_update_f.callback_query.data
        )
        mock_context.user_data.view.posts.user_accepted_share_proposal.assert_called_once_with(
            accepter_tg_name=tg_name,
        )
        mock_posts_sender.share_personal_posts.assert_called_once_with(recipient=mock_context.user_data.current_user, )
        mock_context.user_data.view.cjm.remove_sharing_button.assert_called_once_with(
            message=tg_update_f.effective_message,
        )
        assert result == tg_update_f.callback_query.answer()

    @staticmethod
    def test_decline_button(
            tg_update_f: tg_Update,
            mock_context: MagicMock,
            monkeypatch,
    ):
        monkeypatch.setattr(mock_context.user_data.current_user, 'is_registered', True)
        monkeypatch.setattr(tg_update_f.callback_query, 'data', f'_ {tg_update_f.effective_user.id} 0')
        result = app.tg.ptb.handlers.posts.share_personal_posts_cbk_handler(update=tg_update_f, context=mock_context, )
        mock_context.user_data.view.posts.user_declined_share_proposal.assert_called_once_with(
            posts_sender_tg_user_id=tg_update_f.effective_user.id,
        )
        mock_context.user_data.view.cjm.remove_sharing_button.assert_called_once_with(
            message=tg_update_f.effective_message,
        )
        assert result == tg_update_f.callback_query.answer()


class TestGetMyPersonalPostsCmd:
    @staticmethod
    def test_no_posts(tg_update_f: tg_Update, mock_context: MagicMock, monkeypatch):
        monkeypatch.setattr(mock_context.user_data.current_user.get_personal_posts, 'return_value', [], )
        result = app.tg.ptb.handlers.posts.get_my_personal_posts(_=tg_update_f, context=mock_context, )
        mock_context.user_data.view.posts.no_personal_posts.assert_called_once_with()
        assert result is None

    @staticmethod
    def test_success(tg_update_f: tg_Update, mock_context: MagicMock, monkeypatch):
        with patch.object(app.tg.ptb.classes.posts.VotedPersonalPost, 'convert', autospec=True, ) as mock_convert:
            result = app.tg.ptb.handlers.posts.get_my_personal_posts(_=tg_update_f, context=mock_context, )
        mock_convert.assert_called_once_with(
            posts=mock_context.user_data.current_user.get_personal_posts(),
            clicker=mock_context.user_data.current_user,
            opposite=mock_context.user_data.current_user,
        )
        mock_context.user_data.view.posts.here_your_personal_posts.assert_called_once_with()
        mock_context.user_data.view.posts.show_posts.assert_called_once_with(posts=mock_convert.return_value)
        assert result is None


class TestGetPublicPostCmd:

    @staticmethod
    def test_no_mass_posts(tg_update_f: tg_Update, mock_context: MagicMock, monkeypatch):
        monkeypatch.setattr(mock_context.user_data.current_user.get_new_public_post, 'return_value', None, )
        result = app.tg.ptb.handlers.posts.get_public_post(_=tg_update_f, context=mock_context, )
        # Checks
        mock_context.user_data.current_user.get_new_public_post.assert_called_once_with()
        mock_context.user_data.view.posts.no_mass_posts.assert_called_once_with()
        assert result is None

    @staticmethod
    def test_no_new_posts(tg_update_f: tg_Update, mock_context: MagicMock, monkeypatch):
        monkeypatch.setattr(mock_context.user_data.current_user.get_new_public_post, 'return_value', [], )
        monkeypatch.setattr(mock_context.user_data.current_user.matcher, 'is_user_has_covotes', True, )
        # EXECUTION
        result = app.tg.ptb.handlers.posts.get_public_post(_=tg_update_f, context=mock_context, )
        mock_context.user_data.current_user.get_new_public_post.assert_called_once_with()
        mock_context.user_data.view.posts.no_new_posts.assert_called_once_with()
        assert result is None

    @staticmethod
    def test_success(tg_update_f: tg_Update, mock_context: MagicMock, ):
        result = app.tg.ptb.handlers.posts.get_public_post(_=tg_update_f, context=mock_context, )
        mock_context.user_data.current_user.get_new_public_post.assert_called_once_with()
        mock_context.user_data.view.posts.show_post.assert_called_once_with(
            post=mock_context.user_data.current_user.get_new_public_post.return_value,
        )
        mock_context.user_data.current_user.upsert_shown_post.assert_called_once_with(
            new_message_id=mock_context.user_data.view.posts.show_post.return_value.message_id,
            public_post=mock_context.user_data.current_user.get_new_public_post.return_value,
        )
        assert result is None


class TestGetPendingPublicPostsCmd:

    @staticmethod
    def test_success(tg_update_f: tg_Update, mock_context: MagicMock, monkeypatch, ):
        with patch.object(
                app.tg.ptb.services.PublicPost,
                'get_pending_posts',
                autospec=True,
        ) as mock_get_pending_posts:
            result = app.tg.ptb.handlers.posts.get_pending_public_posts_handler(_=tg_update_f, context=mock_context, )
        mock_get_pending_posts.assert_called_once_with(connection=mock_context.user_data.current_user.connection, )
        mock_context.user_data.view.posts.show_pendings.assert_called_once_with(
            posts=mock_get_pending_posts.return_value,
        )

        assert result is None

    @staticmethod
    def test_no_posts(tg_update_f: tg_Update, mock_context: MagicMock, monkeypatch):
        with patch.object(
                app.tg.ptb.services.PublicPost,
                'get_pending_posts',
                autospec=True,
                return_value=None,
        ) as mock_get_pending_posts:
            result = app.tg.ptb.handlers.posts.get_pending_public_posts_handler(_=tg_update_f, context=mock_context, )
        mock_get_pending_posts.assert_called_once_with(connection=mock_context.user_data.current_user.connection, )
        mock_context.user_data.view.posts.no_pending_posts.assert_called_once_with()

        assert result is None


class TestPublicPostMassSendingHandlerCmd:

    @staticmethod
    def test_no_mass_posts(
            mock_context: MagicMock,
            patched_ptb_public_post: app.tg.ptb.classes.posts.PublicPost,
            monkeypatch,
    ):
        monkeypatch.setattr(patched_ptb_public_post.read_mass, 'return_value', None, )
        result = app.tg.ptb.handlers.posts.public_post_mass_sending_handler(_=typing_Any, context=mock_context, )
        # Checks
        patched_ptb_public_post.read_mass.assert_called_once_with()
        mock_context.user_data.view.posts.no_mass_posts.assert_called_once_with()

        assert result is None

    @staticmethod
    def test_success(
            mock_context: MagicMock,
            patched_ptb_public_post: app.tg.ptb.classes.posts.PublicPost,
            monkeypatch,
    ):
        result = app.tg.ptb.handlers.posts.public_post_mass_sending_handler(_=typing_Any, context=mock_context, )
        # Checks
        patched_ptb_public_post.read_mass.assert_called_once_with()
        mock_context.user_data.view.say_ok.assert_called_once_with()
        mock_context.dispatcher.run_async.assert_called_once_with(
            func=patched_ptb_public_post.read_mass.return_value.mass_sending_job,
        )

        assert result is None


class TestPublicPostInChannelHandlerCmd:
    @staticmethod
    def test_no_mass_posts(
            mock_context: MagicMock,
            patched_ptb_channel_public_post: MagicMock,
            monkeypatch,
    ):
        monkeypatch.setattr(patched_ptb_channel_public_post.read_mass, 'return_value', None, )
        result = app.tg.ptb.handlers.posts.public_post_in_channel_handler(_=typing_Any, context=mock_context, )
        # Checks
        patched_ptb_channel_public_post.read_mass.assert_called_once_with()
        mock_context.user_data.view.posts.no_mass_posts.assert_called_once_with()

        assert result is None

    @staticmethod
    def test_success(
            mock_context: MagicMock,
            patched_ptb_channel_public_post: MagicMock,
    ):
        result = app.tg.ptb.handlers.posts.public_post_in_channel_handler(_=typing_Any, context=mock_context, )
        # Checks
        patched_ptb_channel_public_post.read_mass.assert_called_once_with()
        patched_ptb_channel_public_post.read_mass.return_value.show.assert_called_once_with(
            recipient=patched_ptb_channel_public_post.read_mass.return_value.POSTS_CHANNEL_ID,
        )
        mock_context.user_data.view.say_ok.assert_called_once_with()
        assert result is None


class TestRequestPersonalPostCbkHandler:
    """request_personal_post_cbk_handler"""

    @staticmethod
    def body(
            update: tg_Update,
            mock_context: MagicMock,
            mock_ptb_personal_post: MagicMock,
            mock_bot: MagicMock,
    ):
        app.tg.ptb.handlers.posts.request_personal_post_cbk_handler(update=update, context=mock_context, )
        # Checks
        mock_ptb_personal_post.extract_cbk_data.assert_called_once_with(
            callback_data=update.callback_query.data,
        )
        mock_context.user_data.view.cjm.remove_sharing_button.assert_called_once_with(
            message=update.effective_message,
        )
        mock_bot.answer_callback_query.assert_called_once()

    def accept_body(
            self,
            update: tg_Update,
            mock_context: MagicMock,
            mock_ptb_personal_post: MagicMock,
            mock_bot: MagicMock,
            monkeypatch,
    ):
        monkeypatch.setattr(
            mock_ptb_personal_post.extract_cbk_data,
            'return_value',
            [mock_context.user_data.current_user, True, ],
        )
        self.body(
            update=update,
            mock_context=mock_context,
            mock_ptb_personal_post=mock_ptb_personal_post,
            mock_bot=mock_bot,
        )
        mock_context.user_data.current_user.share_personal_posts.assert_called_once_with(
            recipient=mock_context.user_data.current_user,  # The same user is not a problem
        )

    def test_error(
            self,
            tg_update_f: tg_Update,
            mock_context: MagicMock,
            patched_ptb_personal_post: MagicMock,
            mock_ptb_bot: MagicMock,
            patched_logger: MagicMock,
            monkeypatch,
    ):
        monkeypatch.setattr(patched_ptb_personal_post.extract_cbk_data, 'side_effect', Exception, )
        with patch.object(app.tg.ptb.handlers.posts, 'logger', autospec=True, ) as mock_logger:
            self.body(
                update=tg_update_f,
                mock_context=mock_context,
                mock_ptb_personal_post=patched_ptb_personal_post,
                mock_bot=mock_ptb_bot,
            )
        mock_logger.error.assert_called_once()
        mock_context.user_data.view.internal_error.assert_called_once_with()

    def test_decline_button(
            self,
            tg_update_f: tg_Update,
            mock_context: MagicMock,
            patched_ptb_personal_post: MagicMock,
            mock_ptb_bot: MagicMock,
            monkeypatch,
    ):
        mock_recipient = mock_context.user_data.current_user
        monkeypatch.setattr(patched_ptb_personal_post.extract_cbk_data, 'return_value', [mock_recipient, False, ])
        # Execution
        self.body(
            update=tg_update_f,
            mock_context=mock_context,
            mock_ptb_personal_post=patched_ptb_personal_post,
            mock_bot=mock_ptb_bot,
        )
        # Checks
        mock_context.user_data.view.posts.user_declined_request_proposal.assert_called_once_with(
            posts_recipient_tg_user_id=mock_recipient.tg_user_id
        )

    def test_no_sender_posts(
            self,
            tg_update_f: tg_Update,
            mock_context: MagicMock,
            patched_ptb_personal_post: MagicMock,
            mock_ptb_bot: MagicMock,
            monkeypatch,
    ):
        monkeypatch.setattr(mock_context.user_data.current_user.share_personal_posts, 'return_value', False, )
        # Execution
        self.accept_body(
            update=tg_update_f,
            mock_context=mock_context,
            mock_ptb_personal_post=patched_ptb_personal_post,
            mock_bot=mock_ptb_bot,
            monkeypatch=monkeypatch,
        )
        # Checks
        mock_context.user_data.view.posts.no_personal_posts.assert_called_once_with()
        mock_context.user_data.view.posts.sender_has_no_personal_posts.assert_called_once_with(
            recipient_tg_user_id=mock_context.user_data.current_user.tg_user_id,
        )

    def test_accept_button(
            self,
            tg_update_f: tg_Update,
            mock_context: MagicMock,
            patched_ptb_personal_post: MagicMock,
            mock_ptb_bot: MagicMock,
            monkeypatch,
    ):
        # Execution
        self.accept_body(
            update=tg_update_f,
            mock_context=mock_context,
            mock_ptb_personal_post=patched_ptb_personal_post,
            mock_bot=mock_ptb_bot,
            monkeypatch=monkeypatch,
        )
        # Checks
        mock_context.user_data.view.posts.user_accepted_request_proposal.assert_called_once_with(
            posts_recipient_tg_user_id=mock_context.user_data.current_user.tg_user_id,
        )


class TestUpdatePublicPostStatusCbkHandler:
    """update_public_post_status_cbk"""

    @staticmethod
    @pytest.mark.parametrize(argnames='status', argvalues=app.tg.ptb.classes.posts.PublicPost.Status)
    def test_pending_button(
            tg_update_f: tg_Update,
            mock_context: MagicMock,
            status: app.tg.ptb.classes.posts.PublicPost.Status,
            monkeypatch,
    ):
        post_id = 1
        monkeypatch.setattr(tg_update_f.callback_query, 'data', f'_ {post_id} {status}')
        with patch.object(app.tg.ptb.classes.posts, 'PublicPost', autospec=True, ) as mock_PublicPost:
            result = app.tg.ptb.handlers.posts.update_public_post_status_cbk(update=tg_update_f, context=mock_context, )
        mock_PublicPost.read.assert_called_once_with(
            post_id=post_id,
            connection=mock_context.user_data.current_user.connection,
        )
        mock_PublicPost.read.return_value.Status.assert_called_once_with(status)
        mock_PublicPost.read.return_value.update_status.assert_called_once_with(
            status=mock_PublicPost.read.return_value.Status.return_value
        )
        mock_context.user_data.view.say_ok.assert_called_once_with()

        assert result == tg_update_f.callback_query.answer()

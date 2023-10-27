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
from unittest.mock import ANY
from typing import TYPE_CHECKING

import pytest

import app.structures.base
import app.exceptions
import app.models.votes
import app.models.users
import app.tg.ptb.classes
import app.tg.ptb.classes.posts
import app.tg.ptb.handlers.votes

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    # noinspection PyPackageRequirements
    from telegram import Update as tg_Update


class TestPublicVoteCbkHandler:

    @staticmethod
    @pytest.mark.parametrize("error", [Exception, app.exceptions.UnknownPostType])
    def test_not_found(
            tg_update_f: MagicMock,
            mock_context: MagicMock,
            patched_actions: MagicMock,
            patched_ptb_public_vote: MagicMock,
            error: Exception,
    ):
        patched_actions.callback_to_post.side_effect = error
        app.tg.ptb.handlers.votes.public_vote_cbk_handler(update=tg_update_f, context=mock_context, )
        patched_actions.callback_to_post.assert_called_once_with(update=tg_update_f, context=mock_context, )
        mock_context.user_data.view.posts.voting_internal_error.assert_called_once_with(
            tooltip=tg_update_f.callback_query,
        )
        mock_context.user_data.current_user.set_vote.assert_not_called()
        mock_context.dispatcher.run_async.assert_not_called()

    @staticmethod
    def test_declined(
            tg_update_f: tg_Update,
            mock_context: MagicMock,
            patched_actions: MagicMock,
            patched_ptb_public_vote: MagicMock,
    ):
        mock_context.user_data.current_user.set_vote.return_value = False
        # Execution
        app.tg.ptb.handlers.votes.public_vote_cbk_handler(update=tg_update_f, context=mock_context, )
        # Checks
        patched_actions.callback_to_post.assert_called_once_with(update=tg_update_f, context=mock_context, )
        mock_context.user_data.current_user.set_vote.assert_called_once_with(
            vote=patched_ptb_public_vote.callback_to_vote.return_value,
            post=patched_actions.callback_to_post.return_value,
        )
        mock_context.dispatcher.run_async.assert_not_called()

    @staticmethod
    def test_accepted(
            tg_update_f: tg_Update,
            mock_context: MagicMock,
            patched_actions: MagicMock,
            patched_ptb_public_vote: MagicMock,
    ):
        mock_context.user_data.current_user.set_vote.return_value = True
        # Execution
        app.tg.ptb.handlers.votes.public_vote_cbk_handler(update=tg_update_f, context=mock_context, )
        # Checks
        patched_actions.callback_to_post.assert_called_once_with(update=tg_update_f, context=mock_context, )
        mock_context.user_data.current_user.set_vote.assert_called_once_with(
            vote=patched_ptb_public_vote.callback_to_vote.return_value,
            post=patched_actions.callback_to_post.return_value,
        )
        pytest.skip("Commented. Not in use?")
        mock_context.dispatcher.run_async.assert_called_once_with(
            func=patched_actions.callback_to_post.return_value.update_votes_mass_job,
        )


class TestChannelPublicVoteCbkHandler:
    @staticmethod
    @pytest.mark.parametrize("error", [Exception, app.exceptions.UnknownPostType])
    def test_not_found(
            tg_update_f: MagicMock,
            mock_context: MagicMock,
            patched_actions: MagicMock,
            patched_ptb_public_vote: MagicMock,
            error: Exception,
    ):
        patched_actions.callback_to_post.side_effect = error
        app.tg.ptb.handlers.votes.channel_public_vote_cbk_handler(update=tg_update_f, context=mock_context, )
        patched_actions.callback_to_post.assert_called_once_with(update=tg_update_f, context=mock_context, )
        mock_context.user_data.view.posts.voting_internal_error.assert_called_once_with(
            tooltip=tg_update_f.callback_query,
        )
        mock_context.user_data.current_user.set_vote.assert_not_called()
        mock_context.dispatcher.run_async.assert_not_called()

    @staticmethod
    def test_declined(
            tg_update_f: tg_Update,
            mock_context: MagicMock,
            patched_actions: MagicMock,
            patched_ptb_public_vote: MagicMock,
    ):
        mock_context.user_data.current_user.set_vote.return_value = False
        # Execution
        app.tg.ptb.handlers.votes.channel_public_vote_cbk_handler(update=tg_update_f, context=mock_context, )
        # Checks
        patched_actions.callback_to_post.assert_called_once_with(update=tg_update_f, context=mock_context, )
        mock_context.user_data.current_user.set_vote.assert_called_once_with(
            vote=patched_ptb_public_vote.callback_to_vote.return_value,
            post=patched_actions.callback_to_post.return_value,
        )
        patched_actions.callback_to_post.return_value.update_poll_keyboard.assert_not_called()

    @staticmethod
    def test_accepted(
            tg_update_f: tg_Update,
            mock_context: MagicMock,
            patched_actions: MagicMock,
            patched_ptb_public_vote: MagicMock,
    ):
        mock_context.user_data.current_user.set_vote.return_value = True
        # Execution
        app.tg.ptb.handlers.votes.channel_public_vote_cbk_handler(update=tg_update_f, context=mock_context, )
        # Checks
        patched_actions.callback_to_post.assert_called_once_with(update=tg_update_f, context=mock_context, )
        mock_context.user_data.current_user.set_vote.assert_called_once_with(
            vote=patched_ptb_public_vote.callback_to_vote.return_value,
            post=patched_actions.callback_to_post.return_value,
        )
        patched_actions.callback_to_post.return_value.update_poll_keyboard.assert_called_once_with(
            message_id=tg_update_f.callback_query.message.message_id,
        )


class TestPersonalVoteCbkHandler:

    @staticmethod
    def test_voting_internal_error(
            tg_update_f: tg_Update,
            mock_context: MagicMock,
            patched_ptb_personal_vote: MagicMock,
            patched_actions: MagicMock,
            patched_logger: MagicMock,
            monkeypatch,
    ):
        tg_update_f.callback_query.data = f'_ 1 +1'  # Any number
        patched_actions.callback_to_post.side_effect = app.exceptions.PostNotFound
        # Execution
        app.tg.ptb.handlers.votes.personal_vote_cbk_handler(update=tg_update_f, context=mock_context, )
        # Checks
        patched_ptb_personal_vote.callback_to_vote.assert_called_once_with(
            user=mock_context.user_data.current_user,
            callback=tg_update_f.callback_query,
        )
        patched_actions.callback_to_post.assert_called_once_with(update=tg_update_f, context=mock_context, )
        patched_logger.error.assert_called_once_with(ANY, )  # Any cuz error instance created in run time
        mock_context.user_data.view.posts.voting_internal_error.assert_called_once_with(
            tooltip=tg_update_f.callback_query,
        )

    @staticmethod
    def test_post_not_found(
            tg_update_f: tg_Update,
            mock_context: MagicMock,
            patched_actions: MagicMock,
            patched_ptb_personal_vote: MagicMock,
    ):
        tg_update_f.callback_query.data = f'_ 1 +1'  # Any number
        patched_actions.callback_to_post.side_effect = app.exceptions.PostNotFound()
        # Execution
        app.tg.ptb.handlers.votes.personal_vote_cbk_handler(update=tg_update_f, context=mock_context, )
        # Checks
        patched_ptb_personal_vote.callback_to_vote.assert_called_once_with(
            user=mock_context.user_data.current_user,
            callback=tg_update_f.callback_query,
        )
        patched_actions.callback_to_post.assert_called_once_with(update=tg_update_f, context=mock_context, )

    @staticmethod
    @pytest.mark.parametrize(argnames='post_id', argvalues=['+1', '-1'])
    def test_declined(
            tg_update_f: tg_Update,
            mock_context: MagicMock,
            patched_actions: MagicMock,
            patched_ptb_personal_vote,
            post_id: str,
            monkeypatch,
    ):
        monkeypatch.setattr(mock_context.user_data.current_user.set_vote, 'return_value', False)
        tg_update_f.callback_query.data = f'_ 2 {post_id}'  # "2" is opposite_tg_user_id, post_id is any number
        # Execution
        app.tg.ptb.handlers.votes.personal_vote_cbk_handler(update=tg_update_f, context=mock_context, )
        # Checks
        patched_ptb_personal_vote.callback_to_vote.assert_called_once_with(
            user=mock_context.user_data.current_user,
            callback=tg_update_f.callback_query,
        )
        patched_actions.callback_to_post.assert_called_once_with(update=tg_update_f, context=mock_context, )
        mock_context.user_data.current_user.set_vote.assert_called_once_with(
            vote=patched_ptb_personal_vote.callback_to_vote.return_value,
            post=patched_actions.callback_to_post.return_value,
        )
        patched_actions.callback_to_post.return_value.update_poll_keyboard.assert_not_called()

    @staticmethod
    @pytest.mark.parametrize(argnames='post_id', argvalues=['+1', '-1'])
    def test_accepted(
            tg_update_f: tg_Update,
            mock_context: MagicMock,
            patched_actions: MagicMock,
            patched_ptb_personal_vote,
            post_id: str,
            monkeypatch,
    ):
        mock_user = patched_ptb_personal_vote.Mapper.User.return_value
        tg_update_f.callback_query.data = f'_ 2 {post_id}'  # "2" is opposite_tg_user_id, post_id is any number
        # Execution
        app.tg.ptb.handlers.votes.personal_vote_cbk_handler(update=tg_update_f, context=mock_context, )
        # Checks
        patched_ptb_personal_vote.callback_to_vote.assert_called_once_with(
            user=mock_context.user_data.current_user,
            callback=tg_update_f.callback_query,
        )
        patched_actions.callback_to_post.assert_called_once_with(update=tg_update_f, context=mock_context, )
        mock_context.user_data.current_user.set_vote.assert_called_once_with(
            vote=patched_ptb_personal_vote.callback_to_vote.return_value,
            post=patched_actions.callback_to_post.return_value,
        )
        patched_ptb_personal_vote.Mapper.User.assert_called_once_with(tg_user_id=2, )
        mock_user.get_vote.assert_called_once_with(post=patched_actions.callback_to_post.return_value, )
        patched_actions.callback_to_post.return_value.update_poll_keyboard.assert_called_once_with(
            clicker_vote=patched_ptb_personal_vote.callback_to_vote.return_value,
            opposite_vote=mock_user.get_vote.return_value,
        )

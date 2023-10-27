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
import telegram.error

import app.tg.ptb.config
import app.tg.ptb.classes.posts
import app.tg.ptb.services

from tests.conftest import raise_side_effect

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    import app.structures.base


class TestBotPublicPost:
    class TestPublicPostMassSendingJob:
        """test_public_post_mass_sending_job"""

        @staticmethod
        @pytest.mark.parametrize(
            argnames='error',
            argvalues=(telegram.error.BadRequest(message='foo'), telegram.error.Unauthorized(message='foo'),),
        )
        def test_error(mock_ptb_bot_public_post: MagicMock, error: telegram.error.TelegramError, ):
            """Send post to group of users (job because most likely usage is inside PTB job (another thread))"""
            mock_ptb_bot_public_post.send.side_effect = error
            with (
                patch.object(
                    app.tg.ptb.services.System,
                    'read_all_users_ids',
                    return_value=[1],
                ) as mock_read_all_users_ids,
                patch.object(app.tg.ptb.services.System.Mapper.PublicVote, 'CRUD', autospec=True, ) as mock_crud,
            ):
                app.tg.ptb.services.System.BotPublicPost.mass_send_job(bot_post=mock_ptb_bot_public_post, )
            mock_read_all_users_ids.assert_called_once_with()
            mock_ptb_bot_public_post.send.assert_called_once_with(recipient=1)
            mock_crud.upsert_message_id.assert_not_called()

    @staticmethod
    def test_success(mock_ptb_bot_public_post: MagicMock):
        """Send post to group of users (job because most likely usage is inside PTB job (another thread))"""
        with (
            patch.object(app.tg.ptb.services.System.Mapper.PublicVote, 'CRUD') as mock_crud,
            patch.object(
                app.tg.ptb.services.System,
                'read_all_users_ids',
                return_value=[1],
            ) as mock_read_all_users_ids,
        ):
            app.tg.ptb.services.System.BotPublicPost.mass_send_job(bot_post=mock_ptb_bot_public_post, )
        mock_read_all_users_ids.assert_called_once_with()
        mock_ptb_bot_public_post.send.assert_called_once_with(recipient=1)
        mock_crud.read.assert_called_once_with(
            post_id=mock_ptb_bot_public_post.post_id,
            tg_user_id=1,
            connection=app.tg.ptb.services.System.user.connection
        )
        mock_ptb_bot_public_post.remove_old_user_post.assert_called_once_with(
            tg_user_id=1,
            message_id=mock_crud.read.return_value['message_id'],
        )
        mock_crud.upsert_message_id.assert_called_once_with(
            tg_user_id=1,
            post_id=mock_ptb_bot_public_post.post_id,
            new_message_id=mock_ptb_bot_public_post.send.return_value.message_id,
            connection=app.tg.ptb.services.System.user.connection,
        )
        app.tg.ptb.config.Config.sleep_function.assert_called_once_with(1)
        app.tg.ptb.config.Config.sleep_function.reset_mock()

    @staticmethod
    def test_get_voted_users(mock_ptb_bot_public_post: MagicMock, ):
        result = app.tg.ptb.services.System.BotPublicPost.get_voted_users(post=mock_ptb_bot_public_post, )
        mock_ptb_bot_public_post.get_voted_users.assert_called_once_with(
            connection=app.tg.ptb.services.System.BotPublicPost.System.user.connection
        )
        assert result == mock_ptb_bot_public_post.get_voted_users.return_value


class TestMassUpdateKeyboardJob:
    """mass_update_keyboard_job"""

    @staticmethod
    @pytest.mark.parametrize(
        argnames='error',
        argvalues=(telegram.error.BadRequest(message='foo'), telegram.error.Unauthorized(message='foo'),),
    )
    def test_error(
            mock_ptb_bot_public_post: MagicMock,
            error: telegram.error.TelegramError,
            monkeypatch,
    ):
        monkeypatch.setattr(mock_ptb_bot_public_post.update_poll_keyboard, 'side_effect', raise_side_effect(e=error, ))
        with (
            patch.object(
                app.tg.ptb.services.BotPublicPost,
                'get_voted_users',
                return_value=[mock_ptb_bot_public_post.author],
                autospec=True,
            ) as mock_get_voted_users,
            patch.object(
                app.tg.ptb.services.BotPublicPost.System.Mapper.PublicVote,
                'read',
                autospec=True,
            ) as mock_read,
        ):
            result = app.tg.ptb.services.BotPublicPost.mass_update_keyboard_job(bot_post=mock_ptb_bot_public_post, )
            # Checks
            mock_get_voted_users.assert_called_once_with(post=mock_ptb_bot_public_post, )
            mock_read.assert_called_once_with(
                post_id=mock_ptb_bot_public_post.post_id,
                user=mock_get_voted_users.return_value[0],
            )
            mock_ptb_bot_public_post.update_poll_keyboard.assert_called_once_with(
                clicker_vote=mock_read.return_value,
            )
            # noinspection PyUnresolvedReferences
            app.tg.ptb.config.Config.sleep_function.assert_not_called()
            assert result == []

    @staticmethod
    def test_success(mock_ptb_bot_public_post: MagicMock, ):
        with (
            patch.object(
                app.tg.ptb.services.BotPublicPost,
                'get_voted_users',
                return_value=[mock_ptb_bot_public_post.author],
                autospec=True,
            ) as mock_get_voted_users,
            patch.object(
                app.tg.ptb.services.BotPublicPost.System.Mapper.PublicVote,
                'read',
                autospec=True,
            ) as mock_read,
        ):
            result = app.tg.ptb.services.BotPublicPost.mass_update_keyboard_job(
                bot_post=mock_ptb_bot_public_post,
            )
            # Checks
            mock_get_voted_users.assert_called_once_with(post=mock_ptb_bot_public_post, )
            mock_read.assert_called_once_with(
                post_id=mock_ptb_bot_public_post.post_id,
                user=mock_get_voted_users.return_value[0],
            )
            mock_ptb_bot_public_post.update_poll_keyboard.assert_called_once_with(
                clicker_vote=mock_read.return_value,
            )
            # noinspection PyUnresolvedReferences
            app.tg.ptb.config.Config.sleep_function.assert_called_once_with(1)
            assert result == [mock_ptb_bot_public_post.update_poll_keyboard.return_value]
            # noinspection PyUnresolvedReferences
            app.tg.ptb.config.Config.sleep_function.reset_mock()

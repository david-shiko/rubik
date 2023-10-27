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
from unittest.mock import Mock, patch, call
from typing import TYPE_CHECKING, Any as typing_Any
import pytest

# noinspection PyPackageRequirements
from telegram import InlineKeyboardMarkup as tg_IKM, InlineKeyboardButton as tg_IKB
# noinspection PyPackageRequirements
import telegram.error

from app.exceptions import PostNotFound
from app.models.base.votes import VoteBase
from app.tg.ptb.classes import posts
from app.tg.ptb.config import PUBLIC_VOTE_CBK_S, PERSONAL_VOTE_CBK_S, UPDATE_PUBLIC_POST_STATUS_CBK_S

from tests.conftest import raise_side_effect

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    # noinspection PyPackageRequirements
    from telegram import CallbackQuery
    from app.tg.ptb.classes.votes import PublicVote, PersonalVote
    from app.tg.ptb.classes.users import User


class TestPostBase:
    class TestCallbackToPost:
        """test_callback_to_post"""

        @staticmethod
        def test_success(tg_callback_query_f: CallbackQuery, ):
            tg_callback_query_f.data = '1'
            # create=True - Set read method dynamically cuz it not exist for PostBase (can't be used with autospec)
            with patch.object(posts.PostBase, 'read', create=True, ) as mock_read:
                result = posts.PostBase.callback_to_post(callback=tg_callback_query_f, connection=typing_Any, )
            mock_read.assert_called_once_with(post_id=1, connection=typing_Any, )
            assert result == mock_read.return_value

        @staticmethod
        def test_not_found(tg_callback_query_f: CallbackQuery, ):
            tg_callback_query_f.data = '1'
            with (
                pytest.raises(PostNotFound),
                # create=True - Set read method dynamically cuz it not exist for PostBase (can't be used with autospec)
                patch.object(posts.PostBase, 'read', create=True, return_value=None, ) as mock_read,
            ):
                posts.PostBase.callback_to_post(callback=tg_callback_query_f, connection=typing_Any, )
            mock_read.assert_called_once_with(post_id=1, connection=typing_Any, )


class TestBotPostBase:
    """posts.BotPostBase"""

    @staticmethod
    @pytest.fixture(scope='function', )
    def mock_vote(ptb_user_s: User, ):
        yield Mock(value=None, user=ptb_user_s, Value=VoteBase.Value, )

    @staticmethod
    @pytest.fixture(scope='function', )
    def mock_post():
        yield Mock(post_id=1, NEG_EMOJI='-', POS_EMOJI='+', MARK_VOTE='️️️️🔹️', )

    class TestRemoveOldUserPost:
        """test_remove_old_user_post"""

        @staticmethod
        @pytest.mark.parametrize(
            argnames='error',
            argvalues=(
                    telegram.error.BadRequest(message='foo', ),
                    telegram.error.Unauthorized(message='foo', ),
                    telegram.error.TimedOut,
            ), )
        def test_error(patched_ptb_bot: MagicMock, error: telegram.error.TelegramError, monkeypatch, ):
            monkeypatch.setattr(patched_ptb_bot.delete_message, 'side_effect', raise_side_effect(e=error, ))
            result = posts.BotPostBase.remove_old_user_post(tg_user_id=1, message_id=2, )
            patched_ptb_bot.delete_message.assert_called_with(chat_id=1, message_id=2, )
            assert result is None

        @staticmethod
        def test_success(patched_ptb_bot: MagicMock, ):
            result = posts.BotPostBase.remove_old_user_post(tg_user_id=1, message_id=2, )
            patched_ptb_bot.delete_message.assert_called_with(chat_id=1, message_id=2, )
            assert result == patched_ptb_bot.delete_message.return_value

    @staticmethod
    @pytest.mark.parametrize(
        "vote_value, neg_btn_text, pos_btn_text",
        [
            (VoteBase.Value.NEGATIVE, '-️️️️🔹️', '+'),
            (VoteBase.Value.ZERO, '-', '+'),
            (VoteBase.Value.POSITIVE, '-', '+️️️️🔹️'),
        ],
    )
    def test_get_keyboard(
            mock_post: MagicMock,
            mock_vote: MagicMock,
            vote_value: VoteBase.Value,
            neg_btn_text: str,
            pos_btn_text: str,
            monkeypatch,
    ):
        monkeypatch.setattr(mock_vote, 'value', vote_value)
        expected_keyboard = tg_IKM(
            [[
                tg_IKB(text=neg_btn_text, callback_data="foo 1 -1"),
                tg_IKB(text=pos_btn_text, callback_data="foo 1 +1"),
            ]]
        )
        actual_keyboard = posts.BotPostBase._get_keyboard(self=mock_post, clicker_vote=mock_vote, pattern='foo', )
        assert actual_keyboard == expected_keyboard

    @pytest.mark.skip('Removed method')
    class TestUpdatePollKeyboard:
        """test_update_poll_keyboard"""

        @staticmethod
        def test_non_default_args(patched_ptb_bot: MagicMock, mock_post: MagicMock, mock_vote: MagicMock, ):
            result = posts.BotPostBase.update_keyboard(
                self=mock_post,
                clicker_vote=mock_vote,
                pattern='foo',
                message_id=1,
            )
            patched_ptb_bot.edit_message_reply_markup.assert_called_with(
                chat_id=mock_vote.user.tg_user_id,
                message_id=1,
                reply_markup=mock_post.get_keyboard(clicker_vote=mock_vote, pattern='foo', ),
            )
            assert result == patched_ptb_bot.edit_message_reply_markup.return_value

        @staticmethod
        def test_default_args(patched_ptb_bot: MagicMock, mock_post: MagicMock, mock_vote: MagicMock, ):
            result = posts.BotPostBase.update_poll_keyboard(
                self=mock_post,
                clicker_vote=mock_vote,
                pattern='foo',
            )
            patched_ptb_bot.edit_message_reply_markup.assert_called_with(
                chat_id=mock_vote.user.tg_user_id,
                message_id=mock_post.message_id,
                reply_markup=mock_post.get_keyboard(clicker_vote=mock_vote, pattern='foo', ),
            )
            assert result == patched_ptb_bot.edit_message_reply_markup.return_value


class TestBotPublicPost:

    @staticmethod
    def test_get_keyboard_deprecated(mock_ptb_bot_public_post: MagicMock, ):
        expected_keyboard = tg_IKM(
            [[
                tg_IKB(
                    text=f'{mock_ptb_bot_public_post.NEG_EMOJI} {mock_ptb_bot_public_post.dislikes_count}',
                    callback_data=f'{PUBLIC_VOTE_CBK_S} -{mock_ptb_bot_public_post.post_id}',
                ),
                tg_IKB(
                    text=f'{mock_ptb_bot_public_post.POS_EMOJI} {mock_ptb_bot_public_post.likes_count}',
                    callback_data=f'{PUBLIC_VOTE_CBK_S} +{mock_ptb_bot_public_post.post_id}',
                ),
            ]]
        )
        actual_keyboard = posts.BotPublicPost.get_keyboard_deprecated(self=mock_ptb_bot_public_post, )
        assert actual_keyboard == expected_keyboard

    @staticmethod
    def test_get_keyboard(mock_ptb_bot_public_post: MagicMock, ptb_public_vote_s: PublicVote, ):
        with patch.object(posts.BotPostBase, '_get_keyboard', autospec=True) as mock_get_keyboard:
            result = posts.BotPublicPost.get_keyboard(self=mock_ptb_bot_public_post, clicker_vote=ptb_public_vote_s, )
            mock_get_keyboard.assert_called_once_with(
                self=mock_ptb_bot_public_post,
                clicker_vote=ptb_public_vote_s,
                pattern=PUBLIC_VOTE_CBK_S,
            )
            assert result == mock_get_keyboard.return_value

    class TestUpdatePollKeyboard:
        """test_update_poll_keyboard"""

        @staticmethod
        def test_non_default_args(
                mock_ptb_bot_public_post: MagicMock,
                ptb_public_vote_s: PublicVote,
                patched_ptb_bot: MagicMock,
        ):
            result = posts.BotPublicPost.update_poll_keyboard(
                self=mock_ptb_bot_public_post,
                clicker_vote=ptb_public_vote_s,
            )
            mock_ptb_bot_public_post.get_keyboard.assert_called_once_with(clicker_vote=ptb_public_vote_s, )
            patched_ptb_bot.edit_message_reply_markup.assert_called_once_with(
                chat_id=ptb_public_vote_s.user.tg_user_id,
                message_id=1,
                reply_markup=mock_ptb_bot_public_post.get_keyboard.return_value,
            )
            assert result == patched_ptb_bot.edit_message_reply_markup.return_value

        @staticmethod
        def test_default_args(
                mock_ptb_bot_public_post: MagicMock,
                ptb_public_vote_s: PublicVote,
                patched_ptb_bot: MagicMock,
        ):
            result = posts.BotPublicPost.update_poll_keyboard(
                self=mock_ptb_bot_public_post,
                clicker_vote=ptb_public_vote_s,
            )
            mock_ptb_bot_public_post.get_keyboard.assert_called_once_with(clicker_vote=ptb_public_vote_s, )
            patched_ptb_bot.edit_message_reply_markup.assert_called_once_with(
                chat_id=ptb_public_vote_s.user.tg_user_id,
                # message_id=mock_ptb_bot_public_post.message_id,
                message_id=1,
                reply_markup=mock_ptb_bot_public_post.get_keyboard.return_value,
            )
            assert result == patched_ptb_bot.edit_message_reply_markup.return_value


class TestBotPersonalPost:
    """BotPersonalPost"""

    @staticmethod
    @pytest.fixture(scope='function', )
    def post(ptb_personal_post_s: posts.PersonalPost, ):
        yield posts.BotPersonalPost(**vars(ptb_personal_post_s), )

    @staticmethod
    def test_get_keyboard(post: MagicMock, ptb_personal_vote_s: PersonalVote, ):
        with patch.object(posts.BotPostBase, '_get_keyboard', autospec=True) as mock_get_keyboard:
            result = posts.BotPersonalPost.get_keyboard(self=post, clicker_vote=ptb_personal_vote_s, )
        mock_get_keyboard.assert_called_once_with(
            self=post,
            clicker_vote=ptb_personal_vote_s,
            pattern=PERSONAL_VOTE_CBK_S,
        )
        assert result == mock_get_keyboard.return_value

    @staticmethod
    def test_keyboard_output(ptb_public_post_s: posts.PublicPost, ):
        expected_keyboard = tg_IKM(
            [[
                tg_IKB(
                    text=ptb_public_post_s.POS_EMOJI,
                    callback_data=f'{PUBLIC_VOTE_CBK_S} -{ptb_public_post_s.post_id}',
                ),
                tg_IKB(
                    text=ptb_public_post_s.NEG_EMOJI,
                    callback_data=f'{PUBLIC_VOTE_CBK_S} +{ptb_public_post_s.post_id}',
                ),
            ]]
        )
        actual_keyboard = posts.PublicPost.get_keyboard_deprecated(self=ptb_public_post_s, )
        assert actual_keyboard == expected_keyboard


class TestPublicPost:
    @staticmethod
    def test_send(patched_ptb_bot: MagicMock, mock_ptb_public_post: MagicMock, ptb_public_vote_s: PublicVote, ):
        result = posts.PublicPost.send(self=mock_ptb_public_post, clicker_vote=ptb_public_vote_s, )
        patched_ptb_bot.copy_message.assert_called_once_with(
            chat_id=ptb_public_vote_s.user.tg_user_id,
            from_chat_id=mock_ptb_public_post.STORE_CHANNEL_ID,
            message_id=mock_ptb_public_post.message_id,
            reply_markup=mock_ptb_public_post.get_keyboard.return_value
        )
        mock_ptb_public_post.get_keyboard.assert_called_once_with(clicker_vote=ptb_public_vote_s, )
        assert result == patched_ptb_bot.copy_message.return_value

    @staticmethod
    def test_get_keyboard(mock_ptb_public_post: MagicMock, ptb_public_vote_s: PublicVote, ):
        with patch.object(posts.BotPostBase, '_get_keyboard', autospec=True, ) as mock___get_keyboard:
            result = posts.PublicPost.get_keyboard(self=mock_ptb_public_post, clicker_vote=ptb_public_vote_s, )
        mock___get_keyboard.assert_called_once_with(
            self=mock_ptb_public_post,
            clicker_vote=ptb_public_vote_s,
            pattern=PUBLIC_VOTE_CBK_S,
        )
        assert result == mock___get_keyboard.return_value

    class TestKeyboards:
        class TestShowPending:
            @staticmethod
            def test_build_cbk(mock_ptb_public_post: MagicMock, ):
                result = posts.PublicPost.Keyboards.ShowPending.build_cbk(
                    post=mock_ptb_public_post,
                    status=mock_ptb_public_post.status,
                )
                assert result == (
                    f'{UPDATE_PUBLIC_POST_STATUS_CBK_S} '
                    f'{mock_ptb_public_post.post_id} '
                    f'{mock_ptb_public_post.status}'
                )

            @staticmethod
            def test_update_status(mock_ptb_public_post: MagicMock, ):
                # Call ShowPending.update_status
                actual_keyboard = posts.PublicPost.Keyboards.ShowPending.update_status(post=mock_ptb_public_post, )
                expected_keyboard = tg_IKM(
                    [[
                        tg_IKB(
                            text=posts.PublicPost.Keyboards.ShowPending.BTN_1,
                            callback_data=posts.PublicPost.Keyboards.ShowPending.build_cbk(
                                post=mock_ptb_public_post,
                                status=mock_ptb_public_post.Status.PENDING,
                            )
                        ),
                        tg_IKB(
                            text=posts.PublicPost.Keyboards.ShowPending.BTN_2,
                            callback_data=posts.PublicPost.Keyboards.ShowPending.build_cbk(
                                post=mock_ptb_public_post,
                                status=mock_ptb_public_post.Status.READY_TO_RELEASE,
                            )
                        ),
                    ]]
                )
                assert actual_keyboard.to_dict() == expected_keyboard.to_dict()


class TestChannelPublicPost:
    """Test the ChannelPublicPost class."""

    @staticmethod
    def test_get_keyboard(mock_tg_ptb_channel_public_post: MagicMock, ):
        expected_keyboard = tg_IKM(
            [[
                tg_IKB(
                    text=f'{mock_tg_ptb_channel_public_post.NEG_EMOJI} '
                         f'{mock_tg_ptb_channel_public_post.dislikes_count}',
                    callback_data=f'foo -{mock_tg_ptb_channel_public_post.post_id}',
                ),
                tg_IKB(
                    text=f'{mock_tg_ptb_channel_public_post.POS_EMOJI} {mock_tg_ptb_channel_public_post.likes_count}',
                    callback_data=f'foo +{mock_tg_ptb_channel_public_post.post_id}',
                ),
            ]]
        )
        actual_keyboard = posts.ChannelPublicPost.get_keyboard(self=mock_tg_ptb_channel_public_post, pattern='foo', )
        assert actual_keyboard == expected_keyboard

    @staticmethod
    def test_update_poll_keyboard(patched_ptb_bot: MagicMock, mock_tg_ptb_channel_public_post: MagicMock, ):
        result = posts.ChannelPublicPost.update_poll_keyboard(self=mock_tg_ptb_channel_public_post, message_id=1, )
        patched_ptb_bot.edit_message_reply_markup.assert_called_once_with(
            chat_id=mock_tg_ptb_channel_public_post.POSTS_CHANNEL_ID,
            message_id=1,
            reply_markup=mock_tg_ptb_channel_public_post.get_keyboard(),
        )
        assert result == patched_ptb_bot.edit_message_reply_markup.return_value

    @staticmethod
    def test_show(patched_ptb_bot: MagicMock, mock_tg_ptb_channel_public_post: MagicMock, ):
        result = posts.ChannelPublicPost.show(self=mock_tg_ptb_channel_public_post, )
        patched_ptb_bot.copy_message.assert_called_once_with(
            chat_id=mock_tg_ptb_channel_public_post.POSTS_CHANNEL_ID,
            from_chat_id=mock_tg_ptb_channel_public_post.STORE_CHANNEL_ID,
            message_id=mock_tg_ptb_channel_public_post.message_id,
            reply_markup=mock_tg_ptb_channel_public_post.get_keyboard.return_value,
        )
        mock_tg_ptb_channel_public_post.get_keyboard.assert_called_once_with()
        assert result == patched_ptb_bot.copy_message.return_value


class TestPersonalPost:
    def test_send(
            self,
            ptb_personal_post_s: posts.PersonalPost,
            ptb_personal_vote_s: PersonalVote,
            patched_ptb_bot: MagicMock,
    ):
        with patch.object(posts.PersonalPost, 'get_keyboard', autospec=True) as mock_get_keyboard:
            result = posts.PersonalPost.send(
                self=ptb_personal_post_s,
                clicker_vote=ptb_personal_vote_s,
                opposite_vote=ptb_personal_vote_s,
            )
        patched_ptb_bot.copy_message(
            chat_id=ptb_personal_vote_s.user.tg_user_id,
            from_chat_id=ptb_personal_post_s.STORE_CHANNEL_ID,
            message_id=ptb_personal_post_s.message_id,
            reply_markup=mock_get_keyboard.return_value,
        )
        mock_get_keyboard.assert_called_once_with(
            ptb_personal_post_s,
            clicker_vote=ptb_personal_vote_s,
            opposite_vote=ptb_personal_vote_s,
        )
        assert result == patched_ptb_bot.copy_message.return_value

    @staticmethod
    @pytest.mark.parametrize(
        argnames='pos_btn_text, neg_btn_text, vote_value',
        argvalues=(
                (
                        posts.PersonalPost.LIKE,
                        f'{posts.PersonalPost.NEG_EMOJI}{posts.PersonalPost.MARK_VOTE}{posts.PersonalPost.NEG_EMOJI}',
                        posts.PersonalPost.Mapper.Vote.Value.NEGATIVE,
                ),
                (posts.PersonalPost.LIKE, posts.PersonalPost.DISLIKE, posts.PersonalPost.Mapper.Vote.Value.ZERO),
                (
                        f'{posts.PersonalPost.POS_EMOJI}{posts.PersonalPost.MARK_VOTE}{posts.PersonalPost.POS_EMOJI}',
                        posts.PersonalPost.DISLIKE,
                        posts.PersonalPost.Mapper.Vote.Value.POSITIVE,

                )
        ), )
    def test_get_keyboard(  # TODO improve by bind vote value and text in architecture
            ptb_personal_post_s: posts.PersonalPost,
            ptb_personal_vote_s: PersonalVote,
            vote_value: posts.PersonalPost.Mapper.vote.Value,
            pos_btn_text: str,
            neg_btn_text: str,
            monkeypatch,
    ):
        monkeypatch.setattr(ptb_personal_vote_s, 'value', vote_value, )
        cbk = f'{PERSONAL_VOTE_CBK_S} {ptb_personal_vote_s.user.tg_user_id} {{}}{ptb_personal_post_s.post_id}'
        expected_keyboard = tg_IKM(
            [[

                tg_IKB(text=neg_btn_text, callback_data=cbk.format('-'), ),
                tg_IKB(text=pos_btn_text, callback_data=cbk.format('+'), ),
            ]]
        )
        actual_keyboard = posts.PersonalPost.get_keyboard(
            self=ptb_personal_post_s,
            clicker_vote=ptb_personal_vote_s,
            opposite_vote=ptb_personal_vote_s,
        )
        assert actual_keyboard == expected_keyboard

    class TestShare:
        """share"""

        @staticmethod
        @pytest.mark.parametrize(
            argnames='error',
            argvalues=(telegram.error.BadRequest(message='foo', ), telegram.error.Unauthorized(message='foo', )),
        )
        def test_error(
                mock_ptb_personal_post: MagicMock,
                mock_ptb_user: MagicMock,
                patched_logger: MagicMock,
                error: telegram.error.TelegramError,
        ):
            mock_ptb_personal_post.send.side_effect = raise_side_effect(e=error, )
            result = posts.PersonalPost.share(
                self=mock_ptb_personal_post, post_sender=mock_ptb_user, post_recipient=mock_ptb_user, )
            # Check get_vote calls
            assert mock_ptb_user.get_vote.call_args_list == [
                call(post=mock_ptb_personal_post, ),
                call(post=mock_ptb_personal_post, ),
            ]
            assert mock_ptb_personal_post.remove_old_user_post.call_args_list == [
                call(tg_user_id=mock_ptb_user.tg_user_id, message_id=mock_ptb_user.get_vote.return_value.message_id, ),
                call(tg_user_id=mock_ptb_user.tg_user_id, message_id=mock_ptb_user.get_vote.return_value.message_id, ),
            ]
            # Check send calls
            mock_ptb_personal_post.send.assert_called_once_with(
                clicker_vote=mock_ptb_user.get_vote.return_value,
                opposite_vote=mock_ptb_user.get_vote.return_value,
            )
            patched_logger.error.assert_called_once_with(error)
            mock_ptb_user.get_vote.return_value.CRUD.upsert_message_id.assert_not_called()
            assert result == error

        @staticmethod
        def test_success(mock_ptb_personal_post: MagicMock, mock_ptb_user: MagicMock, ):
            mock_post_recipient_vote = mock_post_sender_vote = mock_ptb_user.get_vote.return_value  # The same is ok
            posts.PersonalPost.share(
                self=mock_ptb_personal_post,
                post_sender=mock_ptb_user,  # The same is ok
                post_recipient=mock_ptb_user,  # The same is ok
            )
            # Check get_vote calls
            assert mock_ptb_user.get_vote.call_args_list == [
                call(post=mock_ptb_personal_post, ),
                call(post=mock_ptb_personal_post, ),
            ]
            assert mock_ptb_personal_post.remove_old_user_post.call_args_list == [
                call(tg_user_id=mock_ptb_user.tg_user_id, message_id=mock_post_sender_vote.message_id, ),
                call(tg_user_id=mock_ptb_user.tg_user_id, message_id=mock_post_recipient_vote.message_id, ),
            ]
            # Check send calls
            assert mock_ptb_personal_post.send.call_args_list == [
                call(clicker_vote=mock_post_sender_vote, opposite_vote=mock_post_recipient_vote, ),
                call(clicker_vote=mock_post_recipient_vote, opposite_vote=mock_post_sender_vote, ),
            ]
            # Check upsert_message_id calls
            assert mock_ptb_user.get_vote.return_value.upsert.call_args_list == [
                call(message_id=mock_ptb_personal_post.send.return_value.message_id, ),
                call(message_id=mock_ptb_personal_post.send.return_value.message_id, ),
            ]

    @staticmethod
    def test_update_poll_keyboard(
            mock_ptb_personal_post: posts.PersonalPost,
            ptb_personal_vote_s: PersonalVote,
            patched_ptb_bot: MagicMock,
    ):
        result = posts.PersonalPost.update_poll_keyboard(
            self=mock_ptb_personal_post,
            clicker_vote=ptb_personal_vote_s,
            opposite_vote=ptb_personal_vote_s,
        )
        patched_ptb_bot.edit_message_reply_markup.assert_called_once_with(
            chat_id=ptb_personal_vote_s.user.tg_user_id,
            message_id=ptb_personal_vote_s.message_id,
            reply_markup=mock_ptb_personal_post.get_keyboard(
                clicker_vote=ptb_personal_vote_s,
                opposite_vote=ptb_personal_vote_s,
            )
        )
        assert result == patched_ptb_bot.edit_message_reply_markup.return_value


class TestVotedPublicPost:
    @staticmethod
    def test_send(mock_tg_ptb_voted_public_post: MagicMock, patched_ptb_bot: MagicMock, ):
        result = posts.VotedPublicPost.send(self=mock_tg_ptb_voted_public_post, )
        mock_tg_ptb_voted_public_post.post.send.assert_called_once_with(
            clicker_vote=mock_tg_ptb_voted_public_post.clicker_vote,
        )
        assert result == mock_tg_ptb_voted_public_post.post.send.return_value


class TestVotedPersonalPost:
    @staticmethod
    def test_send(mock_tg_ptb_voted_personal_post: MagicMock, patched_ptb_bot: MagicMock, ):
        result = posts.VotedPersonalPost.send(self=mock_tg_ptb_voted_personal_post, )
        patched_ptb_bot.copy_message.assert_called_once_with(
            chat_id=mock_tg_ptb_voted_personal_post.clicker_vote.user.tg_user_id,
            from_chat_id=mock_tg_ptb_voted_personal_post.post.STORE_CHANNEL_ID,
            message_id=mock_tg_ptb_voted_personal_post.post.message_id,
            reply_markup=mock_tg_ptb_voted_personal_post.post.get_keyboard.return_value
        )
        assert result == patched_ptb_bot.copy_message.return_value

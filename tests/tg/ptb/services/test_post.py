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
from typing import TYPE_CHECKING, Type, Any as typing_Any

import pytest
# noinspection PyPackageRequirements
from telegram import InlineKeyboardMarkup as tg_IKM, InlineKeyboardButton as tg_IKB

from app.exceptions import UnknownPostType
from app.tg.ptb import constants
from app.tg.ptb.config import REQUEST_PERSONAL_POSTS_CBK_S, ACCEPT_PERSONAL_POSTS_CBK_S
from app.tg.ptb.services import PersonalPost, Post

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from app.tg.ptb.classes.posts import (
        PersonalPostInterface as PtbPersonalPostInterface,
        PublicPostInterface as PtbPublicPostInterface,
    )


class TestPostBase:
    @staticmethod
    # @pytest.mark.skip
    def test_prepare_posts(
            ptb_public_post_s: PtbPublicPostInterface,
            ptb_personal_post_s: PtbPersonalPostInterface,
            mock_user_f: MagicMock,
    ):
        result = Post.prepare_for_send(
            posts=[ptb_public_post_s, ptb_personal_post_s, ],
            clicker=mock_user_f,  # The same is ok
            opposite=mock_user_f,  # The same is ok
        )
        assert result == [
            Post.Mapper.VotedPublicPost(
                post=ptb_public_post_s,
                clicker_vote=mock_user_f.get_vote.return_value,
            ),
            Post.Mapper.VotedPersonalPost(
                post=ptb_personal_post_s,
                clicker_vote=mock_user_f.get_vote.return_value,
                opposite_vote=mock_user_f.get_vote.return_value,
            ),
        ]


class TestPersonalPost:
    """Test PersonalPost class."""

    @staticmethod
    def test_build_accept_post_cbk():
        result = PersonalPost.build_accept_post_cbk(sender_tg_user_id=1, flag=2, )
        assert result == f'{ACCEPT_PERSONAL_POSTS_CBK_S} {1} {2}'

    @staticmethod
    def test_get_accept_post_keyboard():
        expected_keyboard = tg_IKM(
            [[
                tg_IKB(
                    text=constants.Shared.Words.DECLINE,
                    callback_data=PersonalPost.build_accept_post_cbk(sender_tg_user_id=1, flag=0, )
                ),
                tg_IKB(
                    text=constants.Shared.Words.ACCEPT,
                    callback_data=PersonalPost.build_accept_post_cbk(sender_tg_user_id=1, flag=1, )
                ),
            ]]
        )
        actual_keyboard = PersonalPost.get_accept_post_keyboard(sender_tg_user_id=1, )
        assert actual_keyboard == expected_keyboard

    @staticmethod
    def test_ask_permission_share_personal_post():
        expected_keyboard = tg_IKM(
            [[
                tg_IKB(
                    text=constants.Shared.Words.DISALLOW,
                    callback_data=f'{REQUEST_PERSONAL_POSTS_CBK_S} {1} 0'
                ),
                tg_IKB(
                    text=constants.Shared.Words.ALLOW,
                    callback_data=f'{REQUEST_PERSONAL_POSTS_CBK_S} {1} 1'
                ),
            ]]
        )

        result = PersonalPost.ask_permission_share_personal_post(tg_user_id=1, )
        assert result == expected_keyboard


class TestPost:
    class TestPrepareForSend:

        @staticmethod
        def body(
                post: PtbPublicPostInterface | PtbPersonalPostInterface,
                mock_ptb_user: MagicMock,
                voted_cls: Type[Post.Mapper.VotedPublicPost | Post.Mapper.VotedPersonalPost],
        ) -> Post.Mapper.VotedPublicPost | Post.Mapper.VotedPersonalPost:
            result = Post.prepare_for_send(
                posts=[post],
                clicker=mock_ptb_user,
                opposite=mock_ptb_user,
            )
            assert len(result) == 1
            result = result[0]
            assert isinstance(result, voted_cls, )
            assert result.post == post
            assert result.clicker_vote == mock_ptb_user.get_vote.return_value
            return result

        def test_unknown(self, ):
            with pytest.raises(expected_exception=UnknownPostType, ):
                self.body(post=typing_Any, mock_ptb_user=typing_Any, voted_cls=typing_Any, )

        def test_public(
                self,
                mock_ptb_user: MagicMock,
                ptb_public_post_s: PtbPublicPostInterface,
        ):
            self.body(
                post=ptb_public_post_s,
                mock_ptb_user=mock_ptb_user,
                voted_cls=Post.Mapper.VotedPublicPost,
            )

        def test_personal(
                self,
                mock_ptb_user: MagicMock,
                ptb_personal_post_s: PtbPersonalPostInterface,
        ):
            result = self.body(
                post=ptb_personal_post_s,
                mock_ptb_user=mock_ptb_user,
                voted_cls=Post.Mapper.VotedPersonalPost,
            )
            assert result.opposite_vote == mock_ptb_user.get_vote.return_value

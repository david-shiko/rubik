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

from app.tg.ptb import keyboards, constants
from app.tg.ptb import services
from app.tg.ptb.views import View

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from app.tg.ptb.classes.posts import PublicPost


def test_no_mass_posts(mock_tg_view_f: MagicMock, ):
    result = View.Posts.no_mass_posts(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Posts.Public.NO_MASS_POSTS
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_no_more_posts(mock_tg_view_f: MagicMock, ):
    result = View.Deprecated.no_more_posts(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Deprecated.NO_MORE_POSTS
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_no_new_posts(mock_tg_view_f: MagicMock, ):
    result = View.Posts.no_new_posts(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Posts.Public.NO_NEW_POSTS,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_no_pending_posts(mock_tg_view_f: MagicMock, ):
    result = View.Posts.no_pending_posts(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Posts.Public.NO_PENDING
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_no_personal_posts(mock_tg_view_f: MagicMock, ):
    result = View.Posts.no_personal_posts(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Posts.Personal.NO_POSTS,
        reply_markup=keyboards.create_personal_post
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_user_accepted_pers_post_share(mock_tg_view_f: MagicMock, ):
    result = View.Posts.user_accepted_share_proposal(self=mock_tg_view_f, accepter_tg_name='foo', )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Posts.Personal.USER_ACCEPTED_SHARE_PROPOSAL.format(ACCEPTER_TG_NAME='foo'),
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_user_accepted_pers_post_request(mock_tg_view_f: MagicMock, ):
    result = View.Posts.user_accepted_request_proposal(self=mock_tg_view_f, posts_recipient_tg_user_id=1, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=1,
        text=constants.Posts.Personal.USER_ACCEPTED_REQUEST_PROPOSAL.format(ACCEPTER_TG_NAME=mock_tg_view_f.tg_name, ),
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_delete_post(mock_tg_view_f: MagicMock, ):
    result = View.Posts.delete_post(self=mock_tg_view_f, message_id=1, )
    mock_tg_view_f.bot.delete_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        message_id=1,
    )
    assert result == mock_tg_view_f.bot.delete_message.return_value


def test_here_your_personal_posts(mock_tg_view_f: MagicMock, ):
    result = View.Posts.here_your_personal_posts(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Posts.Personal.HERE_YOUR_POSTS,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_here_preview_post(mock_tg_view_f: MagicMock, ):
    result = View.Posts.here_post_preview(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Posts.HERE_POST_PREVIEW,
        reply_markup=keyboards.send_cancel,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_show_posts(mock_tg_view_f: MagicMock, ):
    result = View.Posts.show_posts(self=mock_tg_view_f.posts, posts=[typing_Any, ], )
    mock_tg_view_f.posts.show_post.assert_called_once_with(post=typing_Any, )
    assert result == [mock_tg_view_f.posts.show_post.return_value, ]


class TestShowPost:
    """test_show_post"""

    @staticmethod
    def test_send_method_with_no_args(
            mock_tg_view_f: MagicMock,
            mock_ptb_public_post_form: MagicMock,
    ):  # Test just one post is ok
        result = View.Posts.show_post(
            post=mock_ptb_public_post_form,
        )  # TODO recipient not required?
        mock_ptb_public_post_form.send.assert_called_once_with()
        assert result == mock_ptb_public_post_form.send.return_value

    @staticmethod
    def test_send_method_with_args(mock_tg_view_f: MagicMock, mock_tg_ptb_voted_public_post: MagicMock, ):
        # Test just one post is ok
        result = View.Posts.show_post(post=mock_tg_ptb_voted_public_post, )  # TODO recipient not required?
        mock_tg_ptb_voted_public_post.send.assert_called_once_with()
        assert result == mock_tg_ptb_voted_public_post.send.return_value


def test_ask_who_to_request_personal_posts(mock_tg_view_f: MagicMock, ):
    with patch.object(keyboards, 'remove', autospec=True, ) as mock_remove:
        result = View.Posts.ask_who_to_request_personal_posts(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Posts.Personal.WHO_TO_REQUEST,
        reply_markup=mock_remove.return_value,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_ask_permission_to_share_personal_posts(mock_tg_view_f: MagicMock, ):
    with patch.object(
            services.PersonalPost,
            'ask_permission_share_personal_post',
            autospec=True,
    ) as mock_ask_permission_share_personal_post:
        result = View.Posts.ask_permission_to_share_personal_posts(self=mock_tg_view_f, recipient_tg_user_id=1, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=1,
        text=constants.Posts.Personal.NOTIFY_REQUEST_PROPOSAL.format(USER_TG_NAME=mock_tg_view_f.tg_name),
        reply_markup=mock_ask_permission_share_personal_post.return_value,
    )
    mock_ask_permission_share_personal_post.assert_called_once_with(tg_user_id=mock_tg_view_f.tg_user_id, )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_ask_accept_personal_posts(mock_tg_view_f: MagicMock, ):
    with patch.object(
            services.PersonalPost,
            'get_accept_post_keyboard',
            autospec=True,
    ) as mock_get_accept_post_keyboard:
        result = View.Posts.ask_accept_personal_posts(self=mock_tg_view_f, recipient_tg_user_id=1, )
    mock_get_accept_post_keyboard.assert_called_once_with(sender_tg_user_id=mock_tg_view_f.tg_user_id, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=1,
        text=constants.Posts.Personal.NOTIFY_SHARE_PROPOSAL.format(USER_TG_NAME=mock_tg_view_f.tg_name),
        reply_markup=mock_get_accept_post_keyboard.return_value,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_say_personal_post_hello(mock_tg_view_f: MagicMock):
    result = View.Posts.say_personal_post_hello(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Posts.Personal.HELLO,
        reply_markup=keyboards.cancel,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_say_public_post_hello(mock_tg_view_f: MagicMock):
    result = View.Posts.say_public_post_hello(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        text=constants.Posts.Public.HELLO,
        chat_id=mock_tg_view_f.tg_user_id,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_say_success_post(mock_tg_view_f: MagicMock):
    result = View.Posts.say_success_post(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        text=constants.Posts.CREATED_SUCCESSFULLY,
        chat_id=mock_tg_view_f.tg_user_id,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_post_not_found(mock_tg_view_f: MagicMock, ):
    result = View.Posts.post_not_found(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Posts.NOT_FOUND,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_post_to_vote_not_found(mock_tg_view_f: MagicMock, mock_tg_update_f: MagicMock, ):
    result = View.Posts.post_to_vote_not_found(self=mock_tg_view_f, tooltip=mock_tg_update_f.callback_query, )
    mock_tg_update_f.callback_query.answer.assert_called_once_with(
        text=constants.Posts.POST_TO_VOTE_NOT_FOUND,
        show_alert=True,
    )
    assert result == mock_tg_update_f.callback_query.answer.return_value


def test_ask_who_to_share_personal_posts(mock_tg_view_f: MagicMock, ):
    result = View.Posts.ask_who_to_share_personal_posts(self=mock_tg_view_f)
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Posts.Personal.WHO_TO_SHARE,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_cant_send_posts_to_user_help_text(mock_tg_view_f: MagicMock, ):
    result = View.Posts.cant_send_posts_to_user_help_text(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Posts.Personal.CANT_SEND_TO_THIS_USER,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_say_user_got_share_proposal(mock_tg_view_f: MagicMock):
    result = View.Posts.say_user_got_share_proposal(self=mock_tg_view_f.posts, recipient_tg_user_id=1, )
    mock_tg_view_f.posts.shared_view.say_user_got_share_proposal.assert_called_once_with(
        recipient_tg_user_id=1,
    )
    assert result == mock_tg_view_f.posts.shared_view.say_user_got_share_proposal.return_value


def test_say_user_got_request_proposal(mock_tg_view_f: MagicMock):
    result = View.Posts.say_user_got_request_proposal(self=mock_tg_view_f.posts, recipient_tg_user_id=1, )
    mock_tg_view_f.posts.shared_view.say_user_got_request_proposal.assert_called_once_with(
        recipient_tg_user_id=1,
    )
    assert result == mock_tg_view_f.posts.shared_view.say_user_got_request_proposal.return_value


def test_user_declined_share_proposal(mock_tg_view_f: MagicMock):
    result = View.Posts.user_declined_share_proposal(self=mock_tg_view_f.posts, posts_sender_tg_user_id=1, )
    mock_tg_view_f.posts.shared_view.user_declined_share_proposal.assert_called_once_with(
        tg_user_id=1,
        decliner_tg_name=mock_tg_view_f.posts.tg_name
    )
    assert result == mock_tg_view_f.posts.shared_view.user_declined_share_proposal.return_value


def test_user_declined_request_proposal(mock_tg_view_f: MagicMock):
    result = View.Posts.user_declined_request_proposal(self=mock_tg_view_f.posts, posts_recipient_tg_user_id=1, )
    mock_tg_view_f.posts.shared_view.user_declined_request_proposal.assert_called_once_with(
        tg_user_id=1,
        decliner_tg_name=mock_tg_view_f.posts.tg_name,
    )
    assert result == mock_tg_view_f.posts.shared_view.user_declined_request_proposal.return_value


def test_show_pendings(mock_tg_view_f: MagicMock, ptb_public_post_s: PublicPost, ):
    result = View.Posts.show_pendings(self=mock_tg_view_f.posts, posts=[ptb_public_post_s, ])
    mock_tg_view_f.posts.show_pending.assert_called_once_with(post=ptb_public_post_s, )
    assert result == [mock_tg_view_f.posts.show_pending.return_value]


def test_show_pending(mock_tg_view_f: MagicMock, mock_ptb_public_post: MagicMock, ):
    result = View.Posts.show_pending(self=mock_tg_view_f.posts, post=mock_ptb_public_post, )
    mock_tg_view_f.posts.bot.copy_message.assert_called_once_with(
        chat_id=mock_tg_view_f.posts.tg_user_id,
        from_chat_id=mock_ptb_public_post.STORE_CHANNEL_ID,
        message_id=mock_ptb_public_post.message_id,
        reply_markup=mock_ptb_public_post.Keyboards.ShowPending.update_status.return_value
    )
    assert result == mock_tg_view_f.posts.bot.copy_message.return_value


def test_voting_internal_error(mock_tg_update_f: MagicMock, ):
    result = View.Posts.voting_internal_error(tooltip=mock_tg_update_f.callback_query, )
    mock_tg_update_f.callback_query.answer.assert_called_once_with(
        text=constants.INTERNAL_ERROR,
        show_alert=True,
    )
    assert result == mock_tg_update_f.callback_query.answer.return_value


def test_sender_has_no_personal_posts(mock_tg_view_f: MagicMock, ):
    result = View.Posts.sender_has_no_personal_posts(mock_tg_view_f.posts, 1)
    mock_tg_view_f.posts.bot.send_message.assert_called_once_with(
        chat_id=1,
        text=constants.Posts.Personal.SENDER_HAS_NO_POSTS
        )
    assert result == mock_tg_view_f.posts.bot.send_message.return_value

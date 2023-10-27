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

from app.tg.ptb import keyboards
from app.tg.ptb import constants
from app.tg.ptb.views import View
from app.tg.ptb import services
import app.tg.ptb.classes.collections

if TYPE_CHECKING:
    from unittest.mock import MagicMock


def test_no_collections(mock_tg_view_f: MagicMock, ):
    result = View.Collections.no_collections(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Collections.NO_COLLECTIONS,
        reply_markup=keyboards.create_personal_post
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_ask_collections_for_post(mock_tg_view_f: MagicMock, ):
    collection_names = ['foo', 'bar']
    result = View.Collections.ask_collection_for_post(self=mock_tg_view_f, collection_names=collection_names)
    listed_collections = "\n".join(f"{i + 1}. {name}." for i, name in enumerate(collection_names))
    text = (
        f'{constants.Collections.ASK_FOR_NAMES}\n'
        f'{constants.Collections.MAX_NAME_LEN}\n'
        f'{constants.Collections.HERE_YOUR_COLLECTIONS}\n'
        f'{listed_collections}'
    )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=text,
        reply_markup=keyboards.skip_cancel,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_show_collections(mock_tg_view_f: MagicMock, ):
    with patch.object(
            app.tg.ptb.services.Collection.Keyboards,
            'show_many',
            autospec=True,
    ) as mock_show_many:
        result = View.Collections.show_collections(
            self=mock_tg_view_f,
            sender_tg_user_id=1,
            collections=[typing_Any, ],
            text='foo',
        )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text='foo',
        reply_markup=mock_show_many.return_value,
    )
    mock_show_many.assert_called_once_with(
        sender_tg_user_id=1,
        collections=[typing_Any, ],
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_ask_collection(mock_tg_view_f: MagicMock, ):
    result = View.Collections.ask_collection(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Collections.ASK_TO_SHARE,
        reply_markup=keyboards.skip_cancel,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_show_chosen_collections_for_post(mock_tg_view_f: MagicMock, ):
    result = View.Collections.show_chosen_collections_for_post(
        self=mock_tg_view_f,
        collection_names={'foo', },
    )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=f'{app.constants.Collections.SAY_CHOSE_FOR_POST}\nfoo.',  # Remember, set is unordered
        reply_markup=keyboards.finish_cancel,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_here_collection_posts(mock_tg_view_f: MagicMock, ):
    result = View.Collections.here_collection_posts(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Collections.HERE_POSTS,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_ask_accept_collections(mock_tg_view_f: MagicMock, ):
    with patch.object(
            app.tg.ptb.services.Collection.Keyboards,
            'accept_collections',
            autospec=True,
    ) as mock_accept_collections:
        result = View.Collections.ask_accept_collections(
            self=mock_tg_view_f, recipient_tg_user_id=1, collections_ids={1, 2, 3, },
        )
    mock_accept_collections.assert_called_once_with(
        sender_tg_user_id=mock_tg_view_f.tg_user_id,
        collections_ids={1, 2, 3, },
    )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=1,
        text=constants.Collections.NOTIFY_SHARE_PROPOSAL.format(USER_TG_NAME=mock_tg_view_f.tg_name),
        reply_markup=mock_accept_collections.return_value,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_no_posts_in_collection(mock_tg_view_f: MagicMock, ):
    result = View.Collections.no_posts_in_collection(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        text=constants.Collections.NO_POSTS,
        chat_id=mock_tg_view_f.tg_user_id,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_ask_who_to_share(mock_tg_view_f: MagicMock, ):
    result = View.Collections.ask_who_to_share(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        chat_id=mock_tg_view_f.tg_user_id,
        text=constants.Collections.WHO_TO_SHARE
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


def test_collections_to_share_not_chosen(mock_tg_view_f: MagicMock, ):
    result = View.Collections.collections_to_share_not_chosen(self=mock_tg_view_f, )
    mock_tg_view_f.bot.send_message.assert_called_once_with(
        text=constants.Collections.COLLECTIONS_TO_SHARE_NOT_CHOSE,
        chat_id=mock_tg_view_f.tg_user_id,
        reply_markup=keyboards.finish_cancel,
    )
    assert result == mock_tg_view_f.bot.send_message.return_value


class TestShowCollectionPosts:
    @staticmethod
    def test_empty_posts(mock_tg_view_f: MagicMock, ):
        View.Collections.show_collection_posts(self=mock_tg_view_f.collections, posts=[])
        mock_tg_view_f.collections.no_posts_in_collection.assert_called_once_with()

    @staticmethod
    def test_with_posts(mock_tg_view_f: MagicMock, ptb_public_post_s: app.tg.ptb.classes.posts.PublicPost):
        View.Collections.show_collection_posts(self=mock_tg_view_f.collections, posts=[ptb_public_post_s])
        mock_tg_view_f.collections.here_collection_posts.assert_called_once_with()
        mock_tg_view_f.collections.posts_view.show_posts.assert_called_once_with(posts=[ptb_public_post_s])


def test_show_collections_to_recipient(mock_tg_view_f: MagicMock, ):
    with patch.object(services, 'Collection', autospec=True, ) as mock_collection_cls:
        result = View.Collections.show_collections_to_recipient(
            self=mock_tg_view_f.collections,
            collections=[typing_Any, ],
            sender_tg_user_id=1,
        )

    # Assertions
    mock_collection_cls.Keyboards.set.assert_called_once_with(
        collections=[typing_Any, ],
        keyboard=mock_collection_cls.Mapper.Model.Keyboards.ShowPostsForRecipient
    )
    mock_tg_view_f.collections.show_collections.assert_called_once_with(
        collections=[typing_Any, ],
        sender_tg_user_id=1,
        text=constants.Collections.HERE_SHARED,
    )
    assert result == mock_tg_view_f.collections.show_collections.return_value


def test_show_my_collections(mock_tg_view_f: MagicMock, ):
    with patch.object(services, 'Collection', autospec=True) as mock_collection_cls:
        result = View.Collections.show_my_collections(
            self=mock_tg_view_f.collections,
            collections=[typing_Any, ],
        )
    mock_collection_cls.Keyboards.set.assert_called_once_with(
        collections=[typing_Any, ],
        keyboard=mock_collection_cls.Mapper.Model.Keyboards.Show
    )
    mock_tg_view_f.collections.show_collections.assert_called_once_with(
        collections=[typing_Any, ],
        text=constants.Collections.HERE_YOUR_COLLECTIONS,
    )
    assert result == mock_tg_view_f.collections.show_collections.return_value


def test_shared_collections_not_found(mock_tg_view_f: MagicMock, ):
    result = View.Collections.shared_collections_not_found(self=mock_tg_view_f.collections, )
    mock_tg_view_f.collections.bot.send_message.assert_called_once_with(
        text=constants.Collections.SHARED_COLLECTIONS_NOT_FOUND,
        chat_id=mock_tg_view_f.collections.tg_user_id,
    )
    assert result == mock_tg_view_f.collections.bot.send_message.return_value


def test_recipient_accepted_share_proposal(mock_tg_view_f: MagicMock, ):
    View.Collections.recipient_accepted_share_proposal(self=mock_tg_view_f.collections, sender_tg_user_id=1, )
    mock_tg_view_f.collections.bot.send_message.assert_called_once_with(
        chat_id=1,
        text=constants.Collections.USER_ACCEPTED_SHARE_PROPOSAL.format(
            ACCEPTER_TG_NAME=mock_tg_view_f.collections.tg_name,
        ), )


def test_recipient_declined_share_proposal(mock_tg_view_f: MagicMock, ):
    View.Collections.recipient_declined_share_proposal(self=mock_tg_view_f.collections, sender_tg_user_id=1, )
    mock_tg_view_f.collections.shared_view.user_declined_request_proposal.assert_called_once_with(
            tg_user_id=1,
            decliner_tg_name=mock_tg_view_f.collections.tg_name,
        )

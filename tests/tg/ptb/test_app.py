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

from typing import TYPE_CHECKING, Type
from pathlib import PosixPath
from unittest.mock import patch, mock_open, create_autospec

import pytest

from app.forms import post

from app.tg.ptb.services import Collection
from app.tg.ptb.classes.posts import ChannelPublicPost
from app.tg.ptb.handlers.mix import error_handler
from app.tg.ptb import services, ptb_app, handlers_definition, config

if TYPE_CHECKING:
    from unittest.mock import MagicMock

COLLECTIONS = {"collection_name": [{"path": PosixPath("path/to/file"), "text": "caption_text"}, ], }


def test_read_and_upload_post_to_tg_server(mock_ptb_bot: MagicMock, ):
    with patch("builtins.open", mock_open(read_data="foo")):
        result = ptb_app.read_and_upload_post_to_tg_server(bot=mock_ptb_bot, post=COLLECTIONS['collection_name'][0])
    mock_ptb_bot.send_photo.assert_called_once_with(
        chat_id=ChannelPublicPost.STORE_CHANNEL_ID,
        photo='foo',
        caption="caption_text",
    )
    assert result == mock_ptb_bot.send_photo.return_value


@pytest.mark.parametrize(
    argnames='post_cls, prefix',
    argvalues=(
            (post.PublicPost, services.Collection.NamePrefix.PUBLIC,),
            (post.PersonalPost, services.Collection.NamePrefix.PERSONAL,),
    ), )
def test_create_default_collections_with_posts(
        # patched_ptb_bot: MagicMock,
        mock_ptb_bot: MagicMock,
        prefix: services.Collection.NamePrefix,
        post_cls: Type,
):

    with (
        patch.object(
            ptb_app, "read_and_upload_post_to_tg_server",
            autospec=True,
        ) as mock_read_and_upload_post_to_tg_server,
        patch.object(post, post_cls.__name__, autospec=True, ) as mock_post_cls,  # Patch class
        patch.object(Collection, 'get_defaults_names', autospec=True, return_value=[], ) as mock_get_defaults_names,
        patch.object(Collection, 'create_default', autospec=True, ) as mock_create_default,
    ):
        ptb_app.create_default_collections_with_posts(
            bot=mock_ptb_bot,
            collections=COLLECTIONS,
            post_cls=mock_post_cls,
        )
        mock_get_defaults_names.assert_called_once_with(prefix=prefix, )
        mock_read_and_upload_post_to_tg_server.assert_called_once_with(
            bot=mock_ptb_bot,
            post=COLLECTIONS['collection_name'][0],
        )
        mock_post_cls.assert_called_once_with(
            author=services.System.user,
            message_id=mock_read_and_upload_post_to_tg_server.return_value.message_id,
        )
        mock_create_default.assert_called_once_with(
            name="collection_name",
            posts=[mock_post_cls.return_value.create.return_value],  # Replace ANY with the actual id of the post
            prefix=prefix,
        )


class TestCreatePtbApp:
    @staticmethod
    @pytest.mark.parametrize(
        argnames='mock_handler',
        argvalues=(  # Multiple different types of handler
                create_autospec(spec=handlers_definition.start_handler_cmd, spec_set=True, ),
                create_autospec(spec=handlers_definition.faq_handler_cmd, spec_set=True, ),
        ), )
    def test_handlers_passed(mock_ptb_bot: MagicMock, mock_handler: MagicMock, ):
        handlers = [{'handler': mock_handler}]
        error_handlers = [{'error_handler': create_autospec(spec=error_handler, spec_set=True, )}]
        with (
            patch.object(ptb_app, 'Updater', autospec=True, ) as mock_Updater,
            patch.object(ptb_app, 'ContextTypes', autospec=True, ) as mock_ContextTypes,
            patch.object(handlers_definition, 'get_regular_handlers', autospec=True, ) as mock_get_regular_handlers,
            patch.object(handlers_definition, 'get_chs', autospec=True, ) as mock_get_chs,
            patch.object(handlers_definition, 'get_error_handlers', autospec=True, ) as mock_get_error_handlers,
            patch.object(handlers_definition, 'set_handlers', autospec=True, ) as mock_set_handlers,
        ):
            result = ptb_app.create_ptb_app(
                bot=mock_ptb_bot,
                handlers=handlers,
                error_handlers=error_handlers
            )
        mock_ContextTypes.assert_called_once_with(
            context=ptb_app.CustomCallbackContext,
            user_data=ptb_app.CustomUserData,
        )
        mock_Updater.assert_called_once_with(bot=mock_ptb_bot, context_types=mock_ContextTypes.return_value, )
        mock_get_regular_handlers.assert_not_called()
        mock_get_chs.assert_not_called()
        mock_get_error_handlers.assert_not_called()
        mock_set_handlers.assert_called_once_with(
            dispatcher=mock_Updater.return_value.dispatcher,
            handlers=handlers,
            error_handlers=error_handlers,
        )
        assert result == mock_Updater.return_value

    @staticmethod
    def test_handlers_not_passed(mock_ptb_bot: MagicMock, ):
        with (
            patch.object(ptb_app, 'Updater', autospec=True, ) as mock_Updater,
            patch.object(ptb_app, 'ContextTypes', autospec=True, ) as mock_ContextTypes,
            patch.object(handlers_definition, 'get_regular_handlers', autospec=True, ) as mock_get_regular_handlers,
            patch.object(handlers_definition, 'get_chs', autospec=True, ) as mock_get_chs,
            patch.object(handlers_definition, 'get_error_handlers', autospec=True, ) as mock_get_error_handlers,
            patch.object(handlers_definition, 'set_handlers', autospec=True, ) as mock_set_handlers,
        ):
            result = ptb_app.create_ptb_app(bot=mock_ptb_bot, )
            mock_ContextTypes.assert_called_once_with(
                context=ptb_app.CustomCallbackContext,
                user_data=ptb_app.CustomUserData,
            )
        mock_Updater.assert_called_once_with(bot=mock_ptb_bot, context_types=mock_ContextTypes.return_value, )
        mock_get_regular_handlers.assert_called_once_with()
        mock_get_chs.assert_called_once_with()
        mock_get_error_handlers.assert_called_once_with()
        mock_set_handlers.assert_called_once_with(
            dispatcher=mock_Updater.return_value.dispatcher,
            handlers=mock_get_regular_handlers.return_value + mock_get_chs.return_value,
            error_handlers=mock_get_error_handlers.return_value,
        )
        assert result == mock_Updater.return_value


@pytest.mark.parametrize(
    argnames='post_cls, create_public, create_personal, collections',
    argvalues=(
            (post.PublicPost, True, False, ptb_app.PUBLIC_COLLECTIONS),
            (post.PersonalPost, False, True, ptb_app.PERSONAL_COLLECTIONS,),
    ), )
def test_configure_app(
        ptb_app_config: config.Config,
        post_cls: Type,
        create_public: bool,
        create_personal: bool,
        collections: dict[str, [{str, PosixPath}]]
):
    with (
        patch.object(ptb_app.db_manager.Postgres, 'create_app_tables', autospec=True) as mock_create_app_tables,
        patch.object(post, post_cls.__name__, autospec=True, ) as mock_post_cls,  # Patch class
        patch.object(
            ptb_app,
            'create_default_collections_with_posts',
            autospec=True
        ) as mock_create_default_collections_with_posts,
    ):

        ptb_app.configure_app(
            config=ptb_app_config,
            create_public_default_collections=create_public,
            create_personal_default_collections=create_personal,
        )
    mock_create_app_tables.assert_called_once_with()
    mock_create_default_collections_with_posts.assert_called_once_with(
        bot=ptb_app_config.bot,
        collections=collections,
        post_cls=mock_post_cls,
    )
    for key, value in vars(ptb_app_config).items():
        assert getattr(ptb_app_config, key) == value

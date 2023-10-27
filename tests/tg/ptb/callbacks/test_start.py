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

# noinspection PyPackageRequirements
from telegram import Update as tg_Update

from app.tg.ptb import services, handlers
from app.tg.ptb.classes.collections import Collection as PtbCollection

if TYPE_CHECKING:
    from unittest.mock import MagicMock


def test_entry_point(mock_context: MagicMock):
    handlers.start.entry_point(_=typing_Any, context=mock_context)
    mock_context.user_data.view.cjm.start_scenario.assert_called_once_with()


class TestGlobalScenario:
    """GlobalScenario"""

    @staticmethod
    def test_entry_point(mock_context: MagicMock, tg_update_f: tg_Update, ):
        with patch.object(services, 'Collection', autospec=True, ) as mock_Collection:
            result = handlers.start.GlobalScenario.entry_point(_=typing_Any, context=mock_context, )
        mock_Collection.get_defaults.assert_called_once_with(
            prefix=mock_Collection.NamePrefix.PUBLIC.value,
        )
        mock_Collection.Keyboards.set.assert_called_once_with(
            collections=mock_Collection.get_defaults.return_value,
            keyboard=mock_Collection.Mapper.Model.Keyboards.Show,
        )
        mock_context.user_data.view.cjm.global_scenario_show_collections.assert_called_once_with(
            collections=mock_Collection.get_defaults.return_value,
        )
        assert result == 0

    @staticmethod
    def test_show_cbk_handler(mock_context: MagicMock, mock_tg_update_f: MagicMock, ):
        with (
            patch.object(handlers.start.GlobalScenario.CBK, 'extract', autospec=True, ) as mock_extract,
            patch.object(services.Post, 'prepare_for_send', autospec=True, ) as mock_prepare_for_send,
            patch.object(PtbCollection, 'get_posts', autospec=True, ) as mock_get_posts,
        ):
            handlers.start.GlobalScenario.show_collection_posts_cbk_handler(
                update=mock_tg_update_f,
                context=mock_context,
            )
        mock_extract.assert_called_once_with(cbk_data=mock_tg_update_f.callback_query.data, )
        mock_get_posts.assert_called_once_with(
            collection_id=mock_extract.return_value,
            connection=mock_context.user_data.current_user.connection,
        )
        mock_prepare_for_send.assert_called_once_with(
            posts=mock_get_posts.return_value,
            clicker=mock_context.user_data.current_user,
            opposite=mock_context.user_data.current_user,
        )
        mock_context.user_data.view.collections.show_collection_posts.assert_called_once_with(
            posts=mock_prepare_for_send.return_value,
        )
        mock_context.user_data.view.cjm.global_scenario_notify_ready_keyword.assert_called_once_with()
        mock_tg_update_f.callback_query.answer.assert_called_once_with()


class TestPersonalScenario:
    """PersonalScenario"""
    test_class = handlers.start.PersonalScenario

    def test_entry_point(self, mock_context: MagicMock, patched_ptb_collection: MagicMock, ):
        with patch.object(services.Collection, 'get_defaults', autospec=True, ) as mock_get_defaults:
            result = self.test_class.entry_point(_=typing_Any, context=mock_context, )
        # Checks
        mock_get_defaults.assert_called_once_with(
            prefix=services.Collection.NamePrefix.PERSONAL.value,
        )
        mock_context.user_data.current_user.get_collections.assert_called_once_with()
        mock_context.user_data.view.notify_ready_keyword.assert_called_with()
        mock_context.user_data.view.cjm.personal_scenario_show_collections.assert_called_with(
            collections=(
                    mock_get_defaults.return_value +
                    mock_context.user_data.current_user.get_collections.return_value
            ),
        )
        assert len(mock_context.user_data.view.mock_calls) == 2
        assert result == 0

    @staticmethod
    def test_test_mark_show_cbk_handler(mock_context: MagicMock, mock_tg_update_f: MagicMock, ):
        # Before
        assert mock_context.user_data.tmp_data.collections_id_to_share == set()
        with (
            patch.object(handlers.start.PersonalScenario.CBK, 'extract', autospec=True, ) as mock_extract,
            patch.object(services.Post, 'prepare_for_send', autospec=True, ) as mock_prepare_for_send,
            patch.object(PtbCollection, 'get_posts', autospec=True, ) as mock_get_posts,
        ):
            handlers.start.PersonalScenario.show_collection_posts_for_sender_cbk_handler(
                update=mock_tg_update_f,
                context=mock_context,
            )
        assert mock_context.user_data.tmp_data.collections_id_to_share == {mock_extract.return_value, }
        mock_extract.assert_called_once_with(cbk_data=mock_tg_update_f.callback_query.data, )
        mock_get_posts.assert_called_once_with(
            collection_id=mock_extract.return_value,
            connection=mock_context.user_data.current_user.connection,
        )
        mock_prepare_for_send.assert_called_once_with(
            posts=mock_get_posts.return_value,
            clicker=mock_context.user_data.current_user,
            opposite=mock_context.user_data.current_user,
        )
        mock_context.user_data.view.collections.show_collection_posts.assert_called_once_with(
            posts=mock_prepare_for_send.return_value,
        )
        mock_context.user_data.view.notify_ready_keyword.assert_called_once_with()
        mock_tg_update_f.callback_query.answer.assert_called_once_with()

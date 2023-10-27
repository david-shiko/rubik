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
from unittest.mock import create_autospec  # Magic need for user_data
from pytest import fixture
from typing import TYPE_CHECKING

# noinspection PyUnresolvedReferences,PyPackageRequirements
from telegram.error import BadRequest as tg_error_BadRequest
import app.tg.ptb.structures

from custom_ptb.callback_context import CustomCallbackContext

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    # noinspection PyUnresolvedReferences,PyPackageRequirements
    import app.tg.ptb.forms.user


@fixture(autouse=True, )
def reset_mock(mock_context: MagicMock, ) -> None:
    mock_context.reset_mock()


@fixture(scope='session')  # Session because need to preserve states inside CH
def mock_context(
        target_s: app.tg.ptb.forms.user.Target,
        mock_ptb_user_s: MagicMock,
        mock_tg_view_s: MagicMock,
        mock_ptb_bot_s: MagicMock,
) -> MagicMock:
    # Using CustomCallbackContext instance causes errors
    mock_context: MagicMock = create_autospec(CustomCallbackContext, spec_set=True, )
    mock_context.bot = mock_ptb_bot_s
    mock_context.user_data.current_user = mock_ptb_user_s
    mock_context.user_data.view = mock_tg_view_s
    mock_context.user_data.tmp_data = app.tg.ptb.structures.CustomUserData.TmpData()
    mock_context.user_data.forms = app.tg.ptb.structures.CustomUserData.Forms()
    yield mock_context

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

from typing import TYPE_CHECKING
from unittest.mock import patch

# noinspection PyPackageRequirements
from telegram import Update

import app.tg.ptb.services

if TYPE_CHECKING:
    # noinspection PyPackageRequirements
    from telegram import Update


def test_create_from_update(tg_update_s: Update, ):  # Used in callback_context ptb func
    with patch.object(app.tg.ptb.services.User.Mapper, 'User', autospec=True, ) as mock_user:
        result = app.tg.ptb.services.User.create_from_update(update=tg_update_s, )
    mock_user.assert_called_once_with(tg_user_id=tg_update_s.effective_user.id, )
    assert result == result

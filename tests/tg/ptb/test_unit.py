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
from unittest.mock import create_autospec
from typing import TYPE_CHECKING

# noinspection PyPackageRequirements
from telegram.ext import Updater

import app.utils

import app.tg.ptb.ptb_app
import app.tg.ptb.structures

if TYPE_CHECKING:
    import app.structures.base


class TestCustomUserData:
    @staticmethod
    def test_repr():
        assert app.tg.ptb.structures.CustomUserData().__repr__()


def test_start_ptb_bot():
    mock_updater = create_autospec(spec=Updater, spec_set=True, )  # It's ok
    app.tg.ptb.ptb_app.start_ptb_bot(updater=mock_updater, idle=True)
    app.tg.ptb.ptb_app.start_ptb_bot(updater=mock_updater, idle=False)
    mock_updater.idle.assert_called_once()
    assert mock_updater.start_polling.call_count == 2


class TestTmpData:
    @staticmethod
    def test_clear():
        tmp_data = app.tg.ptb.structures.CustomUserData.TmpData(
            # post_to_update=1,
            collections_id_to_share={3, 4, },
        )
        tmp_data.clear()
        # assert tmp_data.post_to_update is None
        assert tmp_data.collections_id_to_share == set()

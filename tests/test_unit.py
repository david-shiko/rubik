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
import pytest
from typing import TYPE_CHECKING

import app.utils

import app.tg.ptb.ptb_app
import tests.tg.ptb.functional.utils
import app.tg.ptb.structures

if TYPE_CHECKING:
    import app.structures.base


class TestUniqueKeyDict:
    """
    Inheriting from an UniqueKeyDict forcing pytest to ignore this test class,
    most likely because it's  inherit from builtin (apparently).
    See https://stackoverflow.com/q/73846809/14190526
    """

    @staticmethod
    def test_assign_success(unique_key_dict: app.structures.base.UniqueKeyDict):
        unique_key_dict['egg'] = 'egg'
        assert unique_key_dict == {'egg': 'egg'}

    @staticmethod
    def test_update_restriction_success(unique_key_dict: app.structures.base.UniqueKeyDict):
        unique_key_dict['egg'] = 'egg'
        with pytest.raises(app.structures.base.DuplicateKeyError):
            unique_key_dict.update({'egg': 'egg'})

    @staticmethod
    def test_force_update_success(unique_key_dict: app.structures.base.UniqueKeyDict):
        unique_key_dict.force_update({'egg': True})
        assert unique_key_dict == {'egg': True}

        unique_key_dict.force_update()
        assert unique_key_dict == {'egg': True}


def test_get_text_cases():
    expected = ['FOO BAR', 'foo bar', 'Foo bar', 'Foo Bar']
    actual = tests.tg.ptb.functional.utils.get_text_cases(texts=['foO baR'])
    assert actual == expected


def test_get_perc():
    assert app.utils.get_perc(num_1=10, num_2=20) == 50
    assert app.utils.get_perc(num_1=20, num_2=10) == 200
    assert app.utils.get_perc(num_1=3, num_2=10) == 30
    # Edge cases
    assert app.utils.get_perc(num_1=-10, num_2=10) == -100
    assert app.utils.get_perc(num_1=-10, num_2=0) == 0
    assert app.utils.get_perc(num_1=-10, num_2=-10) == 100
    assert app.utils.get_perc(num_1=0, num_2=10) == 0
    assert app.utils.get_perc(num_1=0, num_2=0) == 0
    assert app.utils.get_perc(num_1=0, num_2=-10) == 0
    assert app.utils.get_perc(num_1=10, num_2=10) == 100
    assert app.utils.get_perc(num_1=10, num_2=0) == 0
    assert app.utils.get_perc(num_1=10, num_2=-10) == -100

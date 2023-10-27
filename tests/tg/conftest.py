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
from typing import TYPE_CHECKING
from unittest.mock import create_autospec

from pytest import fixture

# noinspection PyPackageRequirements
from telegram import Location

import app.tg.classes.users
import app.tg.forms.user

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from app.models.users import User
    import app.forms.user


@fixture(scope='session')
def tg_profile_s(user_s: User, ) -> app.tg.classes.users.Profile:
    yield app.tg.classes.users.Profile(user=user_s, )


@fixture(scope='session', )
def tg_location() -> Location:
    location = Location(45, 45, )
    yield location


@fixture(scope='function')
def tg_profile_f(user_f: User, ) -> app.tg.classes.users.Profile:
    yield app.tg.classes.users.Profile(user=user_f, )


@fixture(scope='function')
def tg_new_user_f(new_user_f: app.forms.user.NewUser, ) -> app.tg.forms.user.NewUser:
    yield app.tg.forms.user.NewUser(
        fullname=new_user_f.fullname,
        goal=new_user_f.goal,
        gender=new_user_f.gender,
        age=new_user_f.age,
        country=new_user_f.country,
        city=new_user_f.city,
        comment=new_user_f.comment,
        photos=new_user_f.photos,
        user=new_user_f.user,
    )


@fixture(scope='function', )
def mock_tg_new_user_f(
        tg_new_user_f: app.tg.forms.user.NewUser,
) -> MagicMock:
    yield create_autospec(spec=tg_new_user_f, spec_set=True, )


@fixture(scope='function')
def mock_tg_profile_f(tg_profile_s: app.tg.classes.users.Profile, ) -> MagicMock:
    yield create_autospec(spec=tg_profile_s, spec_set=True, )

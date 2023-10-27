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
from typing import TYPE_CHECKING, TypeAlias
from abc import ABC, abstractmethod

import app.constants
import app.models.users
import app.forms.user

if TYPE_CHECKING:
    import app.models.users
    import app.tg.classes.users

Goal: TypeAlias = app.forms.user.NewUser.Goal
Gender: TypeAlias = app.forms.user.NewUser.Gender


class NewUserInterface(app.forms.user.NewUserInterface, ABC):
    @abstractmethod
    def __repr__(self) -> str:
        ...

    @abstractmethod
    def remove_uploaded_photos(self, ) -> str:
        ...


class NewUser(app.forms.user.NewUser, NewUserInterface, ):
    """TG class to register user (keep temporary data and handle it)"""

    def __init__(
            self,
            user: app.models.users.User,
            fullname: str | None,
            goal: Goal | None,
            gender: Gender | None,
            age: int | None,
            country: str | None,
            city: str | None,
            comment: str | None,
            photos: list[str] | None = None
    ):  # Load previous reg values?
        super().__init__(
            user=user,
            fullname=fullname,
            goal=goal,
            gender=gender,
            age=age,
            country=country,
            city=city,
            comment=comment,
            photos=photos
        )

        self.profile: app.tg.classes.users.Profile = app.tg.classes.users.Profile(user=self.user, profile=self, )

    def __repr__(self) -> str:  # pragma: no cover
        return super().__repr__()  # type: ignore[safe-super]

    def handle_photo_text(self, text: str, ) -> str | None:
        text = text.lower().strip()
        if app.constants.Regexp.BACK_R.match(text) and not self.back_btn_disabled:  # Currently always False
            return None
        elif text == app.constants.Reg.Buttons.REMOVE_PHOTOS.lower():
            return self.remove_uploaded_photos()
        elif text == app.constants.Reg.Buttons.USE_ACCOUNT_PHOTOS.lower():
            return self.add_account_photos()
        elif text == app.constants.Shared.Words.FINISH.lower() or app.constants.Regexp.SKIP_R.match(text.lower()):
            return app.constants.Shared.Words.FINISH  # No del on skip
        else:
            return app.constants.Shared.Warn.INCORRECT_FINISH  # raise?

    def remove_uploaded_photos(self, ) -> str:
        """Layer of behavior"""
        result = self.remove_photos()
        if result is True:
            return app.constants.Reg.PHOTOS_REMOVED_SUCCESS
        else:
            return app.constants.Reg.NO_PHOTOS_TO_REMOVE


class TargetInterface(app.forms.user.TargetInterface, ABC):
    CHECKED_EMOJI_CHECKBOX: str
    UNCHECKED_EMOJI_CHECKBOX: str


class Target(app.forms.user.Target, TargetInterface, ):
    CHECKED_EMOJI_CHECKBOX = '☑'
    UNCHECKED_EMOJI_CHECKBOX = '🔲'

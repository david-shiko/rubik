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
from abc import ABC, abstractmethod

from geopy.exc import GeocoderServiceError

from app.postconfig import locator as yandex_locator
# noinspection PyPackageRequirements
from telegram import InlineKeyboardMarkup as tg_IKM, InlineKeyboardButton as tg_IKB

import app.tg.ptb.keyboards
import app.tg.ptb.constants
import app.tg.ptb.config
import app.tg.forms.user
import app.tg.ptb.classes.users

if TYPE_CHECKING:
    import geopy.geocoders.yandex
    # noinspection PyPackageRequirements
    from telegram import (
        PhotoSize,
        ReplyKeyboardMarkup as tg_RKM,
        Location as tg_Location,
    )
    import app.tg.ptb.classes.users


class NewUserInterface(app.tg.forms.user.NewUserInterface, ABC, ):
    @abstractmethod
    def handle_location_geo(self, location: tg_Location) -> None:
        ...

    @abstractmethod
    def handle_photo_tg_object(self, photo: list[PhotoSize], media_group_id: str | None, ) -> str | None:
        ...

    @abstractmethod
    def add_account_photos(self, ) -> str:
        ...

    @abstractmethod
    def is_reply_on_photo(self, media_group_id: str | None) -> bool:
        ...

    @staticmethod
    @abstractmethod
    def convert_tg_photo(photo: list[PhotoSize], ) -> str:
        ...


class NewUser(app.tg.forms.user.NewUser, NewUserInterface, ):
    """TG class to register user (keep temporary data and handle it)"""

    locator: geopy.geocoders.yandex.Yandex = yandex_locator

    def __init__(
            self,
            user: app.tg.ptb.classes.users.User,
            fullname: str | None = None,
            goal: app.structures.base.Goal | None = None,
            gender: app.structures.base.Gender | None = None,
            age: int | None = None,
            country: str | None = None,
            city: str | None = None,
            comment: str | None = None,
            photos: list[str] | None = None,
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
        self.profile: app.tg.ptb.classes.users.Profile = app.tg.ptb.classes.users.Profile(
            user=self.user,
            profile=self,
        )
        self.current_keyboard: tg_RKM = app.tg.ptb.keyboards.original_photo_keyboard
        # For internal usage as condition
        self._old_media_group_id: str | None = None  # String because in TG API it has str type

    def __repr__(self, ) -> str:
        # noinspection PyProtectedMember
        d = super()._repr() | {
            '_old_media_group_id': self._old_media_group_id,
            'current_keyboard': self.current_keyboard,
        }
        return repr({k: v for k, v in d.items() if v is not None})

    def handle_name(self, text: str) -> None:
        """Override base method because here exists account name"""
        text = text.lower()
        if text.startswith(app.tg.ptb.constants.Reg.Buttons.USE_ACCOUNT_NAME.lower()):
            self.fullname = self.user.tg_name
        else:
            super().handle_name(text=text, )

    def handle_location_geo(self, location: tg_Location) -> None:
        # TODO make app location object
        try:
            resolved_location = self.locator.reverse(
                query=f'{location.latitude}, {location.longitude}',
                exactly_one=True,
            )
        except GeocoderServiceError:
            raise app.exceptions.LocationServiceError(location)
        try:  # TODO error prone geo
            str_location = resolved_location.address.split(',')
            self.city = str_location[-2].strip()
            self.country = str_location[-1].strip()
        except IndexError:
            raise app.exceptions.BadLocation(location)

    def handle_photo_tg_object(self, photo: list[PhotoSize], media_group_id: str | None, ) -> str | None:
        """
        Handle ptb photo indeed
        Тут мини баг. Если отправить 2 группы подряд - будет 2 сообщения о превышении,
        потому что после 10 фото альбому назначается новый айди
        """
        converted_photo = self.convert_tg_photo(photo=photo, )
        if self.add_photo(photo=converted_photo, ) is True:
            if self.is_reply_on_photo(media_group_id=media_group_id, ) is True:
                # Change keyboard here?
                return app.tg.ptb.constants.Reg.PHOTO_ADDED_SUCCESS
        else:
            self.current_keyboard = app.tg.ptb.keyboards.remove_photos
            return app.tg.ptb.constants.Reg.TOO_MANY_PHOTOS
        return None

    def add_account_photos(self, ) -> str:
        user_profile_photos = []
        user_profile_photos_obj = app.tg.ptb.config.Config.bot.get_user_profile_photos(
            user_id=self.user.tg_user_id,
            limit=app.tg.ptb.classes.users.User.MAX_PHOTOS_COUNT - len(self.photos),  # TODO warn beforehand
        )
        # Probably wrong type hint that claims that user_profile_photos_obj may be None
        if user_profile_photos_obj is not None:  # Don't use "or" cuz final list should be unpacked anyway (.photos)
            user_profile_photos = user_profile_photos_obj.photos
        if user_profile_photos and user_profile_photos:  # : list[list[PhotoSize]]
            self.current_keyboard = app.tg.ptb.keyboards.remove_photos
            for tg_ptb_photosize_obj in user_profile_photos:
                photo = self.convert_tg_photo(photo=tg_ptb_photosize_obj, )
                if self.add_photo(photo=photo, ) is False:  # is photo added success
                    return app.tg.ptb.constants.Reg.TOO_MANY_PHOTOS
            return app.tg.ptb.constants.Reg.PHOTOS_ADDED_SUCCESS
        else:
            return app.tg.ptb.constants.Reg.NO_PROFILE_PHOTOS

    def is_reply_on_photo(self, media_group_id: str | None) -> bool:
        """media_group_id need to find out is bot should react with message on the send group of photos"""
        result = media_group_id is None or media_group_id != self._old_media_group_id  # None need
        self._old_media_group_id = media_group_id
        return result  # Check should be before assignment

    def remove_uploaded_photos(self, ) -> str:
        """Layer of PTB exactly"""
        if result := super().remove_uploaded_photos():
            self._old_media_group_id = None
            self.current_keyboard = app.tg.ptb.keyboards.original_photo_keyboard
        return result

    @staticmethod
    def convert_tg_photo(photo: list[PhotoSize], ) -> str:
        """TG photo object is list of 4 photos with a different quality, last item is the best quality"""
        return photo[-1].file_id


class TargetInterface(app.tg.forms.user.TargetInterface, ABC, ):
    @abstractmethod
    def get_checkboxes_keyboard(self, ) -> tg_IKM:
        ...


class Target(app.tg.forms.user.Target, TargetInterface, ):

    def convert_checkboxes_emojis(self, ) -> dict[str, str]:
        return {
            key: self.CHECKED_EMOJI_CHECKBOX if value else self.UNCHECKED_EMOJI_CHECKBOX
            for key, value in self.filters.checkboxes.items()
        }

    def get_checkboxes_keyboard(self, ) -> tg_IKM:
        """
        "callback_data" without flag cuz current incoming value just will be swapped
        """
        # Another method cuz easies to test (because checkboxes are dict currently)
        checkboxes_emojis = self.convert_checkboxes_emojis()

        btn_2 = tg_IKB(
            text=f"{checkboxes_emojis['age']} {app.tg.ptb.constants.Search.Checkboxes.AGE_SPECIFIED}",
            callback_data=f"{app.tg.ptb.config.CHECKBOX_CBK_S} age",
        )
        btn_3 = tg_IKB(
            text=f"{checkboxes_emojis['country']} {app.tg.ptb.constants.Search.Checkboxes.COUNTRY_SPECIFIED}",
            callback_data=f"{app.tg.ptb.config.CHECKBOX_CBK_S} country",
        )
        btn_4 = tg_IKB(
            text=f"{checkboxes_emojis['city']} {app.tg.ptb.constants.Search.Checkboxes.CITY_SPECIFIED}",
            callback_data=f"{app.tg.ptb.config.CHECKBOX_CBK_S} city",
        )
        btn_5 = tg_IKB(
            text=f"{checkboxes_emojis['photo']} {app.tg.ptb.constants.Search.Checkboxes.PHOTO_SPECIFIED}",
            callback_data=f"{app.tg.ptb.config.CHECKBOX_CBK_S} photo",
        )
        return tg_IKM([[btn_2, btn_3], [btn_4, btn_5]])

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
from unittest.mock import patch

import app.structures.base
import app.tg.classes.users
import app.tg.forms.user

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    import app.tg.ptb.classes.users


class TestProfile:

    @staticmethod
    def test_convert_goal(tg_profile_f: app.tg.ptb.classes.users.Profile, ):
        translations = (
            app.constants.Reg.Profile.I_WANNA_CHAT,
            app.constants.Reg.Profile.I_WANNA_DATE,
            app.constants.Reg.Profile.I_WANNA_CHAT_AND_DATE,
        )
        for goal, translate in zip(sorted(app.structures.base.Goal), translations, strict=True, ):
            tg_profile_f.user.goal = goal
            result = tg_profile_f.convert_goal()
            assert result == translate

    @staticmethod
    def test_convert_gender_gender(tg_profile_f: app.tg.ptb.classes.users.Profile, ):
        translations = (app.constants.Reg.Profile.I_MALE, app.constants.Reg.Profile.I_FEMALE,)
        for gender, translate in zip(sorted(app.structures.base.Gender), translations, strict=True, ):
            tg_profile_f.user.gender = gender
            result = tg_profile_f.convert_gender()
            assert result == translate

    @staticmethod
    def test_get_data(mock_tg_profile_f: MagicMock, ):
        mock_tg_profile_f.is_loaded = False
        result = app.tg.classes.users.Profile.get_data(self=mock_tg_profile_f, )
        # Checks
        mock_tg_profile_f.load.assert_called_once_with()
        mock_tg_profile_f.get_profile_text.assert_called_once_with()
        mock_tg_profile_f.get_profile_text.assert_called_once_with()
        mock_tg_profile_f.Payload.assert_called_once_with(
            text=mock_tg_profile_f.get_profile_text.return_value,
            photos=mock_tg_profile_f.user.photos,
        )
        assert result == mock_tg_profile_f.Payload.return_value

    @staticmethod
    def test_get_profile_text(tg_profile_f: app.tg.ptb.classes.users.Profile, ):
        nickname_link = f"<a href='tg://user?id={tg_profile_f.user.tg_user_id}'>{tg_profile_f.user.fullname}</a>"
        result = app.tg.classes.users.Profile.get_profile_text(self=tg_profile_f, )
        assert result == (
            f"{app.constants.Shared.Profile.NAME} - {nickname_link}.\n"
            f"{app.constants.Shared.Profile.GOAL} - {app.constants.Reg.Profile.I_WANNA_CHAT}.\n"
            f"{app.constants.Shared.Profile.GENDER} - {app.constants.Reg.Profile.I_MALE}.\n"
            f"{app.constants.Shared.Profile.AGE} - {tg_profile_f.user.age}.\n"
            f"{app.constants.Shared.Profile.LOCATION} - {tg_profile_f.user.country}, {tg_profile_f.user.city}.\n"
            f"{app.constants.Shared.Profile.ABOUT} - {tg_profile_f.user.comment}"  # Pay attention no tailing dot
        )

    @staticmethod
    def test_convert_text(tg_profile_f: app.tg.ptb.classes.users.Profile, ):
        nickname_link = f"<a href='tg://user?id={tg_profile_f.user.tg_user_id}'>{tg_profile_f.user.fullname}</a>"
        result = app.tg.classes.users.Profile.convert_text(self=tg_profile_f, )
        assert result == {
            f"{app.constants.Shared.Profile.NAME}": nickname_link,
            f"{app.constants.Shared.Profile.GOAL}": app.constants.Reg.Profile.I_WANNA_CHAT,
            f"{app.constants.Shared.Profile.GENDER}": app.constants.Reg.Profile.I_MALE,
            f"{app.constants.Shared.Profile.AGE}": tg_profile_f.user.age,
            f"{app.constants.Shared.Profile.LOCATION}": f"{tg_profile_f.user.country}, {tg_profile_f.user.city}",
            f"{app.constants.Shared.Profile.ABOUT}": tg_profile_f.user.comment,
        }

    @staticmethod
    def test_get_db_data(mock_tg_profile_f: MagicMock, ):
        mock_tg_profile_f.user.CRUD.read.return_value = {}
        with patch.object(app.models.mix.Photo.CRUD, 'read', ) as mock_read:
            result = app.tg.classes.users.Profile.get_db_data(self=mock_tg_profile_f, )
        mock_tg_profile_f.user.CRUD.read.assert_called_once_with(
            tg_user_id=mock_tg_profile_f.user.tg_user_id,
            connection=mock_tg_profile_f.user.connection,
        )
        mock_read.assert_called_once_with(
            tg_user_id=mock_tg_profile_f.user.tg_user_id,
            connection=mock_tg_profile_f.user.connection,
        )
        assert result

    @staticmethod
    def test_load(mock_tg_profile_f: MagicMock, ):
        """Set profile data from DB"""
        attrs = ('fullname', 'goal', 'gender', 'age', 'country', 'city', 'comment',)
        [setattr(mock_tg_profile_f.user, attr, None) for attr in attrs]
        mock_tg_profile_f.get_db_data.return_value = {attr: mock_tg_profile_f for attr in attrs}
        app.tg.classes.users.Profile.load(self=mock_tg_profile_f, )  # PHOTO?
        mock_tg_profile_f.get_db_data.assert_called_once_with()
        assert all([getattr(mock_tg_profile_f.user, attr) == mock_tg_profile_f for attr in attrs])


class TestNewUser:

    @staticmethod
    def test_remove_uploaded_photos(mock_tg_new_user_f: MagicMock, ):
        for flag, text in (
                (True, app.constants.Reg.PHOTOS_REMOVED_SUCCESS),
                (False, app.constants.Reg.NO_PHOTOS_TO_REMOVE,),
        ):
            mock_tg_new_user_f.remove_photos.return_value = flag
            result = app.tg.forms.user.NewUser.remove_uploaded_photos(self=mock_tg_new_user_f, )
            mock_tg_new_user_f.remove_photos.assert_called_once_with()
            assert result == text
            mock_tg_new_user_f.reset_mock()

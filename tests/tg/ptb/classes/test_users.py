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

import typing
from unittest.mock import patch
from typing import TYPE_CHECKING, Any as typing_Any

import pytest
from geopy.exc import GeocoderServiceError
# noinspection PyPackageRequirements
from telegram import (
    Location as tg_Location,
    InputMediaPhoto as tg_InputMediaPhoto,
    ParseMode as tg_ParseMode,
)

import app.tg.forms.user
import app.tg.ptb.keyboards
import app.tg.ptb.constants
import app.tg.ptb.classes.posts
import app.tg.ptb.classes.matches

import app.tg.ptb.forms.user

from tests.conftest import raise_side_effect

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    # noinspection PyPackageRequirements
    from telegram import User as tg_ptb_User, PhotoSize as tg_PhotoSize
    import app.tg.ptb.classes.users
    import app.tg.classes.users
    import app.models.users
    from app.structures.base import Covote


class TestPTBProfile:

    @staticmethod
    def test_prepare_photos(mock_ptb_profile: MagicMock, ):
        mock_ptb_profile.user.photos = ['photo_file_tg_id', ]
        result = app.tg.ptb.classes.users.Profile.prepare_photos_to_send(self=mock_ptb_profile, caption='foo', )
        assert result[0].caption == 'foo'
        assert result == [tg_InputMediaPhoto(media='photo_file_tg_id', parse_mode=tg_ParseMode.HTML), ]

    @staticmethod
    def test_send(patched_ptb_bot: MagicMock, mock_ptb_profile: MagicMock, ):
        app.tg.ptb.classes.users.Profile.send(self=mock_ptb_profile)
        mock_ptb_profile.get_data.assert_called_once_with()
        mock_ptb_profile.prepare_photos_to_send.assert_called_once_with(
            caption=mock_ptb_profile.get_data.return_value.text,
        )
        patched_ptb_bot.send_media_group.assert_called_once_with(
            chat_id=mock_ptb_profile.user.tg_user_id,
            media=mock_ptb_profile.prepare_photos_to_send.return_value,
        )


class TestMatch:
    @staticmethod
    def test_show(mock_tg_ptb_match: MagicMock, ):
        app.tg.ptb.classes.matches.Match.show(self=mock_tg_ptb_match, )
        mock_tg_ptb_match.create.assert_called_once_with()


class TestMatcher:
    @staticmethod
    def test_convert_matches(
            mock_ptb_matcher: MagicMock,
            covote: Covote,
            mock_tg_ptb_match: MagicMock,
    ):
        with patch.object(
                app.models.matches.Matcher,
                'convert_matches',
                autospec=True,
                return_value=[mock_tg_ptb_match],
        ) as mock_super_convert_matches:
            result = app.tg.ptb.classes.matches.Matcher.convert_matches(self=mock_ptb_matcher, raw_matches=[covote], )
        mock_super_convert_matches.assert_called_once_with(self=mock_ptb_matcher, raw_matches=[covote], )
        assert all(match.user.profile.is_loaded is False for match in mock_super_convert_matches.return_value)
        assert result == mock_super_convert_matches.return_value


class TestUser:

    @staticmethod
    def test_is_tg_active(ptb_user_s: app.tg.ptb.classes.users.User, monkeypatch, ):
        """Check setter and getter properties is correct"""
        monkeypatch.setattr(ptb_user_s, 'is_tg_active', True)  # Check assignment
        assert ptb_user_s.is_tg_active is True
        monkeypatch.setattr(ptb_user_s, 'tg_user_id', -1)  # <= 0 tg_user_id will cause BadRequest inside
        assert ptb_user_s.is_tg_active is False

    class TestGetTgName:

        @staticmethod
        @pytest.fixture(autouse=True, )
        def reset_patched_ptb_bot(patched_ptb_bot: MagicMock):
            patched_ptb_bot.reset_mock()

        @staticmethod
        def test_by_ptb_user(patched_ptb_bot: MagicMock, tg_ptb_user_f: tg_ptb_User, monkeypatch, ):
            result = app.tg.ptb.classes.users.User.get_tg_name(entity=tg_ptb_user_f, )
            assert len(patched_ptb_bot.mock_calls) == 0
            assert result == f'@{tg_ptb_user_f.username}'

        @staticmethod
        def test_by_tg_user_id(patched_ptb_bot: MagicMock, ):
            # TODO if no username/fullname etc
            result = app.tg.ptb.classes.users.User.get_tg_name(entity=1)
            patched_ptb_bot.get_chat.assert_called_once_with(chat_id=1, timeout=3)
            assert result == f'@{patched_ptb_bot.get_chat.return_value.username}'

        @staticmethod
        def test_no_username(patched_ptb_bot: MagicMock, monkeypatch, ):
            monkeypatch.setattr(patched_ptb_bot.get_chat.return_value, 'username', None, )
            result = app.tg.ptb.classes.users.User.get_tg_name(entity=1)
            patched_ptb_bot.get_chat.assert_called_once_with(chat_id=1, timeout=3)
            assert len(patched_ptb_bot.mock_calls) == 1
            assert result == patched_ptb_bot.get_chat.return_value.full_name

        @staticmethod
        def test_error(patched_ptb_bot: MagicMock, ):
            result = app.tg.ptb.classes.users.User.get_tg_name(entity=-1, )  # tg_user_id <= 0 will cause BadRequest
            patched_ptb_bot.get_chat.assert_called_once_with(chat_id=-1, timeout=3)
            assert len(patched_ptb_bot.mock_calls) == 1
            assert result == ''

    @staticmethod
    def test_posts_not_passed(
            mock_ptb_user: MagicMock,
            mock_ptb_personal_post: MagicMock,
    ):
        mock_ptb_user.get_personal_posts.return_value = [mock_ptb_personal_post]
        app.tg.ptb.classes.users.User.share_personal_posts(self=mock_ptb_user, recipient=typing_Any, )
        mock_ptb_user.get_personal_posts.assert_called_once_with()
        mock_ptb_personal_post.share.assert_called_once_with(post_sender=mock_ptb_user, post_recipient=typing_Any, )

    @staticmethod
    def test_share_collections_posts(mock_ptb_user: MagicMock, mock_ptb_collection: MagicMock, ):
        app.tg.ptb.classes.users.User.share_collections_posts(
            self=mock_ptb_user,
            recipient=mock_ptb_user,
        )
        mock_ptb_user.get_collections.assert_called_once_with()
        mock_ptb_user.share_personal_posts.assert_called_once_with(
            recipient=mock_ptb_user,
            posts=mock_ptb_user.get_collections.return_value[0].posts,
        )


class TestNewUser:

    @staticmethod
    def test_repr(ptb_new_user_f: app.tg.ptb.classes.users.User, ):
        repr(ptb_new_user_f)

    @staticmethod
    def test_handle_name(ptb_new_user_f: app.tg.ptb.forms.user.NewUser, ) -> None:
        """No need to make call assertions on setters if actual == expected"""
        with patch.object(app.tg.forms.user.NewUser, 'handle_name', autospec=True, ) as mock_handle_name:
            app.tg.ptb.forms.user.NewUser.handle_name(self=ptb_new_user_f, text='foo', )
            mock_handle_name.assert_called_once_with(self=ptb_new_user_f, text='foo', )
        ptb_new_user_f.user.tg_name = 'foo'
        ptb_new_user_f.handle_name(text=app.tg.ptb.constants.Reg.Buttons.USE_ACCOUNT_NAME, )
        assert ptb_new_user_f.fullname == ptb_new_user_f.user.tg_name

    @staticmethod
    def test_handle_location_geo_bad_location(mock_ptb_new_user_f: MagicMock, tg_location: tg_Location, ):
        mock_ptb_new_user_f.locator.reverse.return_value.address = ''
        with pytest.raises(expected_exception=app.exceptions.BadLocation):
            app.tg.ptb.forms.user.NewUser.handle_location_geo(self=mock_ptb_new_user_f, location=tg_location, )
        mock_ptb_new_user_f.locator.reverse.assert_called_once_with(
            query=f'{tg_location.latitude}, {tg_location.longitude}',
            exactly_one=True,
        )

    @staticmethod
    def test_handle_location_geo_service_error(mock_ptb_new_user_f: MagicMock, tg_location: tg_Location, ):
        mock_ptb_new_user_f.locator.reverse.side_effect = raise_side_effect(e=GeocoderServiceError, )
        with pytest.raises(expected_exception=app.exceptions.LocationServiceError, ):
            app.tg.ptb.forms.user.NewUser.handle_location_geo(self=mock_ptb_new_user_f, location=tg_location, )
        mock_ptb_new_user_f.locator.reverse.assert_called_once_with(
            query=f'{tg_location.latitude}, {tg_location.longitude}',
            exactly_one=True,
        )

    @staticmethod
    def test_handle_location_geo(mock_ptb_new_user_f: MagicMock, tg_location: tg_Location, ):
        mock_ptb_new_user_f.locator.reverse.return_value.address = 'Ставропольский край, Россия'
        app.tg.ptb.forms.user.NewUser.handle_location_geo(
            self=mock_ptb_new_user_f,
            location=tg_Location(longitude=45, latitude=45),
        )
        mock_ptb_new_user_f.locator.reverse.assert_called_once_with(
            query=f'{tg_location.latitude}, {tg_location.longitude}',
            exactly_one=True,
        )
        assert mock_ptb_new_user_f.country == 'Россия'
        assert mock_ptb_new_user_f.city == 'Ставропольский край'

    class TestHandlePhotoText:
        @staticmethod
        def test_go_back(mock_ptb_new_user_f, ):
            """Btn is disabled currently"""
            result = app.tg.ptb.forms.user.NewUser.handle_photo_text(
                self=mock_ptb_new_user_f,
                text=app.tg.ptb.constants.Shared.Words.BACK,
            )
            assert result == app.tg.ptb.constants.Shared.Warn.INCORRECT_FINISH  # GO back btn is disabled

        @staticmethod
        def test_remove_uploaded_photos(mock_ptb_new_user_f, ):
            result = app.tg.ptb.forms.user.NewUser.handle_photo_text(
                self=mock_ptb_new_user_f,
                text=app.tg.ptb.constants.Reg.Buttons.REMOVE_PHOTOS,
            )
            mock_ptb_new_user_f.remove_uploaded_photos.assert_called_once_with()
            assert result == mock_ptb_new_user_f.remove_uploaded_photos.return_value

        @staticmethod
        def test_use_account_photos(patched_ptb_bot: MagicMock, mock_ptb_new_user_f, ):
            result = app.tg.ptb.forms.user.NewUser.handle_photo_text(
                self=mock_ptb_new_user_f,
                text=app.tg.ptb.constants.Reg.Buttons.USE_ACCOUNT_PHOTOS,
            )
            mock_ptb_new_user_f.add_account_photos.assert_called_once_with()
            assert result == mock_ptb_new_user_f.add_account_photos.return_value

        @staticmethod
        def test_finish_or_skip():
            for text in [app.tg.ptb.constants.Shared.Words.FINISH, app.tg.ptb.constants.Shared.Words.SKIP, ]:
                result = app.tg.ptb.forms.user.NewUser.handle_photo_text(
                    self=typing.Any,
                    text=text,
                )
                assert result == app.tg.ptb.constants.Shared.Words.FINISH  # Skip or Finish should return finish

        @staticmethod
        def test_incorrect_finish():
            result = app.tg.ptb.forms.user.NewUser.handle_photo_text(self=typing.Any, text='foo', )
            assert result == app.tg.ptb.constants.Shared.Warn.INCORRECT_FINISH

    class TestAddAccountPhotos:

        @staticmethod
        def body(patched_ptb_bot: MagicMock, mock_ptb_new_user_f: MagicMock, ):
            mock_ptb_new_user_f.photos = []  # Just apply take len
            result = app.tg.ptb.forms.user.NewUser.add_account_photos(self=mock_ptb_new_user_f, )
            patched_ptb_bot.get_user_profile_photos.assert_called_once_with(
                user_id=mock_ptb_new_user_f.user.tg_user_id,
                limit=app.tg.ptb.forms.user.NewUser.MAX_PHOTOS_COUNT - len(mock_ptb_new_user_f.photos),
            )
            return result

        def test_no_photos(self, patched_ptb_bot: MagicMock, mock_ptb_new_user_f: MagicMock, monkeypatch, ):
            monkeypatch.setattr(patched_ptb_bot.get_user_profile_photos.return_value, 'photos', [], )
            result = self.body(
                patched_ptb_bot=patched_ptb_bot,
                mock_ptb_new_user_f=mock_ptb_new_user_f,
            )
            assert len(mock_ptb_new_user_f.mock_calls) == 0
            assert result == app.tg.ptb.constants.Reg.NO_PROFILE_PHOTOS

        def test_too_many_photos(self, patched_ptb_bot: MagicMock, mock_ptb_new_user_f: MagicMock, monkeypatch, ):
            mock_ptb_new_user_f.add_photo.return_value = False
            monkeypatch.setattr(patched_ptb_bot.get_user_profile_photos.return_value, 'photos', ['foo', ], )
            # BEFORE
            assert mock_ptb_new_user_f.current_keyboard != app.tg.ptb.keyboards.remove_photos
            # EXECUTION
            result = self.body(
                patched_ptb_bot=patched_ptb_bot,
                mock_ptb_new_user_f=mock_ptb_new_user_f,
            )
            # CHECKS
            mock_ptb_new_user_f.convert_tg_photo.assert_called_once_with(photo='foo', )
            mock_ptb_new_user_f.add_photo.assert_called_once_with(
                photo=mock_ptb_new_user_f.convert_tg_photo.return_value,
            )
            assert mock_ptb_new_user_f.current_keyboard == app.tg.ptb.keyboards.remove_photos
            assert result == app.tg.ptb.constants.Reg.TOO_MANY_PHOTOS

        def test_success(self, patched_ptb_bot: MagicMock, mock_ptb_new_user_f: MagicMock, monkeypatch, ):
            monkeypatch.setattr(patched_ptb_bot.get_user_profile_photos.return_value, 'photos', ['foo', ], )
            # BEFORE
            assert mock_ptb_new_user_f.current_keyboard != app.tg.ptb.keyboards.remove_photos
            # EXECUTION
            result = self.body(
                patched_ptb_bot=patched_ptb_bot,
                mock_ptb_new_user_f=mock_ptb_new_user_f,
            )
            # CHECKS
            mock_ptb_new_user_f.convert_tg_photo.assert_called_once_with(photo='foo', )
            mock_ptb_new_user_f.add_photo.assert_called_once_with(
                photo=mock_ptb_new_user_f.convert_tg_photo.return_value,
            )
            assert mock_ptb_new_user_f.current_keyboard == app.tg.ptb.keyboards.remove_photos
            assert result == app.tg.ptb.constants.Reg.PHOTOS_ADDED_SUCCESS

    class TestHandlePhotoTgObject:

        @staticmethod
        def body(tg_ptb_photo: list[tg_PhotoSize], mock_ptb_new_user_f: MagicMock, media_group_id: str, ):
            result = app.tg.ptb.forms.user.NewUser.handle_photo_tg_object(
                self=mock_ptb_new_user_f,
                photo=tg_ptb_photo,
                media_group_id=media_group_id,
            )
            mock_ptb_new_user_f.convert_tg_photo.assert_called_once_with(photo=tg_ptb_photo, )
            mock_ptb_new_user_f.add_photo.assert_called_once_with(
                photo=mock_ptb_new_user_f.convert_tg_photo.return_value,
            )
            return result

        def test_too_many_photos(
                self,
                mock_ptb_new_user_f: MagicMock,
                tg_ptb_photo_s: list[tg_PhotoSize],
        ):
            # BEFORE
            assert mock_ptb_new_user_f.current_keyboard != app.tg.ptb.keyboards.remove_photos
            result = self.body(
                mock_ptb_new_user_f=mock_ptb_new_user_f,
                tg_ptb_photo=tg_ptb_photo_s,
                media_group_id='1',
            )
            assert mock_ptb_new_user_f.current_keyboard == app.tg.ptb.keyboards.remove_photos
            assert result == app.tg.ptb.constants.Reg.TOO_MANY_PHOTOS

        def test_no_reply(
                self,
                mock_ptb_new_user_f: MagicMock,
                tg_ptb_photo_s: list[tg_PhotoSize],
        ):
            mock_ptb_new_user_f.add_photo.return_value = True
            result = self.body(
                mock_ptb_new_user_f=mock_ptb_new_user_f,
                tg_ptb_photo=tg_ptb_photo_s,
                media_group_id='1',
            )
            mock_ptb_new_user_f.is_reply_on_photo.assert_called_once_with(media_group_id='1', )
            assert result is None

        def test_success(
                self,
                mock_ptb_new_user_f: MagicMock,
                tg_ptb_photo_s: list[tg_PhotoSize],
        ):
            mock_ptb_new_user_f.add_photo.return_value = True
            mock_ptb_new_user_f.is_reply_on_photo.return_value = True
            # BEFORE
            assert mock_ptb_new_user_f.current_keyboard != app.tg.ptb.keyboards.remove_photos
            result = self.body(
                mock_ptb_new_user_f=mock_ptb_new_user_f,
                tg_ptb_photo=tg_ptb_photo_s,
                media_group_id='1',
            )
            mock_ptb_new_user_f.is_reply_on_photo.assert_called_once_with(media_group_id='1', )
            assert result == app.tg.ptb.constants.Reg.PHOTO_ADDED_SUCCESS

    @staticmethod
    def test_is_reply_on_photo(ptb_new_user_f: app.tg.ptb.forms.user.NewUser, ):
        # Compare with itself
        assert ptb_new_user_f.is_reply_on_photo(media_group_id=ptb_new_user_f._old_media_group_id) is True
        assert ptb_new_user_f.is_reply_on_photo(media_group_id='500') is True
        assert ptb_new_user_f.is_reply_on_photo(media_group_id='500') is False
        assert ptb_new_user_f.is_reply_on_photo(media_group_id=None) is True
        assert ptb_new_user_f.is_reply_on_photo(media_group_id=None) is True
        assert ptb_new_user_f.is_reply_on_photo(media_group_id='500') is True
        assert ptb_new_user_f._old_media_group_id == '500'  # Assignment every call, just a one check

    @staticmethod
    def test_remove_uploaded_photos(mock_ptb_new_user_f: MagicMock, ):
        with patch.object(
                app.tg.forms.user.NewUser,
                'remove_uploaded_photos',
        ) as mock_remove_uploaded_photos:
            result = app.tg.ptb.forms.user.NewUser.remove_uploaded_photos(self=mock_ptb_new_user_f, )
        mock_remove_uploaded_photos.assert_called_once_with()
        assert mock_ptb_new_user_f._old_media_group_id is None
        assert mock_ptb_new_user_f.current_keyboard == app.tg.ptb.keyboards.original_photo_keyboard
        assert result == mock_remove_uploaded_photos.return_value

    @staticmethod
    def test_convert_tg_photo(tg_ptb_photo_s: list[tg_PhotoSize], ):
        result = app.tg.ptb.forms.user.NewUser.convert_tg_photo(photo=tg_ptb_photo_s)
        assert result == tg_ptb_photo_s[-1].file_id

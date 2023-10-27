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
from string import ascii_lowercase

import app.forms

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from faker import Faker


class TestPublicPostForm:
    @staticmethod
    def test_create(mock_public_post_form: MagicMock, ):
        app.forms.post.PublicPost.create(self=mock_public_post_form, )
        mock_public_post_form.Mapper.PublicPost.create.assert_called_once_with(
            author=mock_public_post_form.author,
            message_id=mock_public_post_form.message_id,
        )


class TestPersonalPostForm:
    @staticmethod
    def test_create(mock_personal_post_form: MagicMock, ):
        app.forms.post.PersonalPost.create(self=mock_personal_post_form, )
        mock_personal_post_form.Mapper.PersonalPost.create.assert_called_once_with(
            author=mock_personal_post_form.author,
            message_id=mock_personal_post_form.message_id,
        )

    @staticmethod
    def test_handle_collection_names(personal_post_form_f: MagicMock, faker: Faker, ):
        assert app.forms.post.PersonalPost.MAX_COLLECTION_NAME_LEN < len(ascii_lowercase)
        expected = {ascii_lowercase[:app.forms.post.PersonalPost.MAX_COLLECTION_NAME_LEN], }
        app.forms.post.PersonalPost.handle_collection_names(self=personal_post_form_f, text=ascii_lowercase, )
        assert personal_post_form_f.collection_names == expected
        assert all((len(name) <= app.forms.post.PersonalPost.MAX_COLLECTION_NAME_LEN for name in expected))

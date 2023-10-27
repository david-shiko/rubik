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

from abc import ABC
from typing import TYPE_CHECKING

import app.forms.post
import app.tg.classes.posts

if TYPE_CHECKING:
    import app.models.users


class PublicPostInterface(app.forms.post.PublicPostInterface, ABC, ):
    STORE_CHANNEL_ID = app.tg.classes.posts.PostsChannels.STORE.value


class PublicPost(app.forms.post.PublicPost, app.tg.classes.posts.PublicPostEmoji, PublicPostInterface, ):
    STORE_CHANNEL_ID: app.tg.classes.posts.PostsChannels.STORE.value


class PersonalPostInterface(app.forms.post.PersonalPostInterface, ABC, ):
    STORE_CHANNEL_ID: app.tg.classes.posts.PostsChannels.STORE.value


class PersonalPost(app.forms.post.PersonalPost, app.tg.classes.posts.PersonalPostEmoji, PersonalPostInterface, ):
    STORE_CHANNEL_ID = app.tg.classes.posts.PostsChannels.STORE.value

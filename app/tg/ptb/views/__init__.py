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
from typing import TYPE_CHECKING, Type

from . import base, search, reg, collections, posts, cjm

if TYPE_CHECKING:
    # noinspection PyPackageRequirements
    from telegram import Bot
    # noinspection PyPackageRequirements
    from telegram.ext import ExtBot
    from app.tg.ptb.classes import users as ptb_users


class View(base.Shared, ):
    Reg: Type[reg.Reg] = reg.Reg
    Search: Type[search.Search] = search.Search
    Collections: Type[collections.Collections] = collections.Collections
    Posts: Type[posts.Posts] = posts.Posts
    CJM: Type[cjm.CJM] = cjm.CJM

    def __init__(self, user: ptb_users.User, bot: Bot | ExtBot, ):
        super().__init__(user=user, bot=bot, )
        self.reg: reg.Reg = self.Reg(user=user, bot=bot, )
        self.search: search.Search = self.Search(user=user, bot=bot, )
        self.posts: posts.Posts = self.Posts(user=user, bot=bot, shared_view=self, )
        self.collections: collections.Collections = self.Collections(
            user=user,
            bot=bot,
            posts_view=self.posts,
            shared_view=self,
        )
        self.cjm: cjm.CJM = cjm.CJM(user=user, bot=bot, collections_view=self.collections, shared_view=self, )

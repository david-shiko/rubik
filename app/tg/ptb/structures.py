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
from typing import TYPE_CHECKING, TypedDict, List, Union, Dict, Any
from dataclasses import dataclass, field, asdict
from abc import ABC, abstractmethod
from pprint import pformat

if TYPE_CHECKING:
    from datetime import timedelta as datetime_timedelta
    from typing_extensions import NotRequired  # External library, built-in from python 3.11
    # noinspection PyPackageRequirements
    from telegram import Update, InlineKeyboardButton as tg_IKB
    # noinspection PyPackageRequirements
    from telegram.ext import Handler
    # noinspection PyPackageRequirements
    from telegram.ext.dispatcher import UT
    # noinspection PyPackageRequirements
    from telegram.ext.utils.types import CCT
    from app.tg.ptb.views import View
    from app.tg.ptb.classes.users import UserInterface
    from app.tg.ptb import forms


class KeyboardInterface(ABC, ):
    @abstractmethod
    def build_callback(self, *args: Any, **kwargs: Any, ) -> str:
        ...

    @abstractmethod
    def build_inline_button(self, *args: Any, **kwargs: Any, ) -> tg_IKB:
        ...

    @classmethod
    @abstractmethod
    def extract_cbk_data(cls, cbk_data: str, ) -> Any:
        ...


@dataclass(slots=True)
class CustomUserData:

    @dataclass(slots=True)
    class TmpData:
        collections_id_to_share: set[int] = field(default_factory=set)
        message_id_to_edit: int | None = None

        def clear(self) -> None:
            # self.post_to_update = None
            self.collections_id_to_share = set()

    @dataclass(slots=True)
    class Forms:
        new_user: forms.user.NewUserInterface | None = None
        target: forms.user.Target | None = None
        post: forms.post.PublicPost | forms.post.PersonalPost | None = None

    view: View = None
    current_user: UserInterface | None = None
    tmp_data: TmpData = TmpData()
    forms: Forms = Forms()

    def __repr__(self):  # pragma: no cover
        return pformat(asdict(self))


# # # TYPE HINTS ONLY # # #
class ConversationHandlerKwargs(TypedDict):  # Not in use
    entry_points: List[Handler[Update, CCT]]
    states: Dict[object, List[Handler[Update, CCT]]]
    fallbacks: List[Handler[Update, CCT]]
    allow_reentry: bool
    per_chat: bool
    per_user: bool
    per_message: bool
    conversation_timeout: Union[float, datetime_timedelta]
    name: str
    persistent: bool
    map_to_parent: Dict[object, object]
    run_async: bool


class DispatcherAddHandlerKwargs(TypedDict):
    handler: Handler[UT, CCT]
    group: NotRequired[int]  # Optional key, see https://docs.python.org/3/library/typing.html#typing.TypedDict

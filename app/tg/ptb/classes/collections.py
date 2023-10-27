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
from typing import TYPE_CHECKING, Type, Iterator, Protocol, Any, TypeVar
from abc import ABC, abstractmethod

# noinspection PyPackageRequirements
from telegram import InlineKeyboardButton as tg_IKB

from app.tg.ptb import config
from app.tg.ptb import structures

import app.tg.classes.collections
import app.tg.ptb.classes.users
import app.tg.ptb.classes.posts

if TYPE_CHECKING:
    import app.structures.type_hints
    from app.tg.ptb.classes import CollectionMapper


class CollectionInterface(app.tg.classes.collections.CollectionInterface, ABC, ):
    Mapper: Type[CollectionMapper]

    class Keyboards(ABC):
        Show: Type[KeyboardInterface]


class KeyboardProtocol(Protocol, ):
    collection: Collection
    current: Type[KeyboardInterface] | None


class KeyboardInterface(KeyboardProtocol, structures.KeyboardInterface, ABC, ):
    @abstractmethod
    def __init__(self, collection: Collection, current: Type[KeyboardInterface] | None): ...


# Need to bypass False positive Pycharm warning
KeyboardInterfaceT = TypeVar('KeyboardInterfaceT', bound=KeyboardInterface, )


class Collection(app.tg.classes.collections.Collection, CollectionInterface, ):
    Mapper: Type[CollectionMapper]

    def __init__(self, *args, **kwargs, ):
        super().__init__(*args, **kwargs, )
        self.keyboards = self.Keyboards(collection=self, )

    class KeyboardsMeta(type):
        def __iter__(cls) -> Iterator[Type[KeyboardInterfaceT]]:
            """Implement usage as list(Keyboards). Useful for tests"""
            for name, attr in vars(cls).items():
                if isinstance(attr, type) and issubclass(attr, KeyboardInterface):
                    yield attr

    class Keyboards(metaclass=KeyboardsMeta, ):  # To add list(Keyboards) feature

        def __init__(self, collection: Collection, current: Type[KeyboardInterfaceT] | None = None, ):
            if current is not None:
                self.current = current(collection=collection, )  # False positive Pycharm warning
            else:
                self.current = None

        class Shared(KeyboardInterface, ):
            def __init__(self, collection: Collection, ):
                """
                Use ref to  collection rather than attrs directly cuz they are mutable.
                Required attrs:
                1. name
                2. collection_id
                """
                self.collection = collection

            def build_callback(self, sender_tg_user_id: int, ) -> str:
                raise NotImplemented

            def build_inline_button(self, sender_tg_user_id: int, ) -> tg_IKB:
                cbk_data = self.build_callback(sender_tg_user_id=sender_tg_user_id, )
                btn = tg_IKB(text=self.collection.name, callback_data=cbk_data, )
                return btn

            @classmethod
            def extract_cbk_data(cls, cbk_data: str, ) -> Any:
                raise NotImplemented

        class Show(Shared, ):
            """For collections recipient"""

            def build_callback(self, sender_tg_user_id: int, ) -> str:
                return f'{config.SHOW_COLLECTION_CBK_S} {self.collection.collection_id}'

            @classmethod
            def extract_cbk_data(cls, cbk_data: str, ) -> int:
                _, str_collection_id = cbk_data.split()
                return int(str_collection_id)

        class MarkAndShow(Shared, ):
            """For collections recipient"""

            def build_callback(self, sender_tg_user_id: int, ) -> str:
                return f'{config.MARK_SHOW_COLLECTION_CBK_S} {self.collection.collection_id}'

            @classmethod
            def extract_cbk_data(cls, cbk_data: str, ) -> int:
                _, str_collection_id = cbk_data.split()
                return int(str_collection_id)

        class ShowPostsForRecipient(Shared, ):
            """Personal scenario. For recipient collections directly via personal scenario"""

            def build_callback(self, sender_tg_user_id: int, ) -> str:
                return f'{config.SHOW_COLLECTION_POSTS_CBK_S} {sender_tg_user_id} {self.collection.collection_id}'

            @classmethod
            def extract_cbk_data(
                    cls,
                    cbk_data: str,
                    user: app.tg.ptb.classes.users.UserInterface | None = None,
            ) -> tuple[app.tg.ptb.classes.users.UserInterface, int]:
                _, str_sender_tg_user_id, str_collection_id = cbk_data.split()
                sender_tg_user_id = int(str_sender_tg_user_id)
                if getattr(user, 'tg_user_id', None) == sender_tg_user_id:
                    sender = user
                else:
                    sender = Collection.Mapper.User(tg_user_id=sender_tg_user_id, )
                return sender, int(str_collection_id)

        class Mark(Shared, ):
            """For user sharing collections directly or via personal scenario"""

            def build_callback(self, sender_tg_user_id: int, ) -> str:
                return f'{config.MARK_COLLECTION_CBK_S} {self.collection.collection_id}'

            @classmethod
            def extract_cbk_data(cls, cbk_data: str, ) -> int:
                _, str_collection_id = cbk_data.split()
                return int(str_collection_id)

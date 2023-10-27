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
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Protocol, Optional, Any

import app.structures.base
from app.db import crud

if TYPE_CHECKING:
    from psycopg2.extensions import connection as pg_ext_connection

"""This class not depends on other classes (not uses them)"""


class UserBaseDC:
    """
    A DataClass representing a user base. This is an example of how you might define such a class.
    """

    # Define the enums for various fields
    Goal = app.structures.base.Goal
    Gender = app.structures.base.Gender
    Age = app.structures.base.Age

    # Define maximum lengths for various fields
    MAX_COMMENT_LEN = 1024
    MAX_USER_NAME_LEN = 64
    MAX_USER_NAME_WORDS = 3
    MAX_COUNTRY_LEN = MAX_CITY_LEN = 32
    MAX_PHOTOS_COUNT = 10

    def __init__(
            self,
            fullname: Optional[str] = None,
            goal: Optional[app.structures.base.Goal] = None,
            gender: Optional[app.structures.base.Gender] = None,
            age: Optional[int] = None,
            country: Optional[str] = None,
            city: Optional[str] = None,
            comment: Optional[str] = None,
            photos: Optional[list[str]] = None,
    ):
        self._fullname: Optional[str] = fullname
        self._goal: Optional[app.structures.base.Goal] = goal
        self._gender: Optional[app.structures.base.Gender] = gender
        self._age: Optional[int] = age
        self._country: Optional[str] = country
        self._city: Optional[str] = city
        self._comment: Optional[str] = comment
        self.photos = photos or []


class UserBasePropertiesProtocol(Protocol):
    """Protocol for UserBase"""

    _fullname: Optional[str]
    _goal: Optional[app.structures.base.Goal]
    _gender: Optional[app.structures.base.Gender]
    _age: Optional[int]
    _country: Optional[str]
    _city: Optional[str]
    _comment: Optional[str]
    photos: list[str]  # Photo is not property but easier t put it here

    @property
    @abstractmethod
    def fullname(self, ) -> Optional[str]: ...

    @fullname.setter
    @abstractmethod
    def fullname(self, value: Optional[str]) -> None: ...

    @property
    @abstractmethod
    def goal(self, ) -> Optional[app.structures.base.Goal]: ...

    @goal.setter
    @abstractmethod
    def goal(self, value: Optional[app.structures.base.Goal]) -> None: ...

    @property
    @abstractmethod
    def gender(self, ) -> Optional[app.structures.base.Gender]: ...

    @gender.setter
    @abstractmethod
    def gender(self, value: Optional[app.structures.base.Gender]) -> None: ...

    @property
    @abstractmethod
    def age(self, ) -> Optional[int]: ...

    @age.setter
    @abstractmethod
    def age(self, value: Optional[int]) -> None: ...

    @property
    @abstractmethod
    def country(self, ) -> Optional[str]: ...

    @country.setter
    @abstractmethod
    def country(self, value: Optional[str]) -> None: ...

    @property
    @abstractmethod
    def city(self, ) -> Optional[str]: ...

    @city.setter
    @abstractmethod
    def city(self, value: Optional[str]) -> None: ...

    @property
    @abstractmethod
    def comment(self, ) -> Optional[str]: ...

    @comment.setter
    @abstractmethod
    def comment(self, value: Optional[str]) -> None: ...

    @abstractmethod
    def _repr(self, ) -> dict[str, Any]: ...

    @abstractmethod
    def __repr__(self, ) -> str: ...


class UserBaseProperties(UserBaseDC, UserBasePropertiesProtocol, ABC, ):

    def _repr(self, ) -> dict[str, Any]:  # Here because repr easiest to debug (attrs not exists on init stage)
        d = {
            'self': object.__repr__(self, ),
            'fullname': self.fullname,
            'goal': self.goal,
            'gender': self.gender,
            'age': self.age,
            'city': self.city,
            'country': self.country,
            'comment': self.comment,
            'photos': self.photos,
        }
        return d

    def __repr__(self, ):  # Here because repr easiest to debug (attrs not exists on init stage). pragma: no cover
        return repr(self._repr())

    @property
    def fullname(self, ) -> Optional[str]:
        return self._fullname

    @fullname.setter
    def fullname(self, value: Optional[str]) -> None:
        if value is not None:
            if len(value) > self.MAX_USER_NAME_LEN:
                raise app.exceptions.IncorrectProfileValue(
                    f"The username length is too long (Maximum is: {self.MAX_USER_NAME_LEN}, used: {len(value)})"
                )
            if (words_count := len(value.split(' '))) > self.MAX_USER_NAME_WORDS:
                raise app.exceptions.IncorrectProfileValue(
                    f"The username has too many words (Maximum is: {self.MAX_USER_NAME_WORDS}), used: {words_count}"
                )
        self._fullname = value

    @property
    def goal(self, ) -> app.structures.base.Goal | None:
        return self._goal

    @goal.setter
    def goal(self, value: app.structures.base.Goal) -> None:
        if value is not None:
            try:  # Better to check via Enum(value) because in Goal require convert
                value = self.Goal(value)
            except ValueError:
                raise app.exceptions.IncorrectProfileValue(f"The goal should be in range {list(self.Goal)}")
        self._goal = value

    @property
    def gender(self, ) -> app.structures.base.Gender | None:
        return self._gender

    @gender.setter
    def gender(self, value: app.structures.base.Gender, ) -> None:
        if value is not None:
            try:  # Better to check via Enum(value) because in Goal require convert
                value = self.Gender(value)
            except ValueError:
                raise app.exceptions.IncorrectProfileValue(f"The gender should be in range {self.Gender}")
        self._gender = value

    @property
    def age(self, ) -> int | None:
        return self._age

    @age.setter
    def age(self, value: int, ) -> None:
        if value is None or isinstance(value, int) and self.Age.MIN <= value <= self.Age.MAX:
            self._age = value
        else:
            raise app.exceptions.IncorrectProfileValue(
                f"The age should be in range {self.Age.MIN, self.Age.MAX}"
            )

    @property
    def country(self, ) -> str | None:
        return self._country

    @country.setter
    def country(self, value: str, ) -> None:
        if value is not None:
            if len(value) > self.MAX_COUNTRY_LEN:
                raise app.exceptions.IncorrectProfileValue(
                    f"The country name length is too long (Maximum is: "
                    f"{self.MAX_COUNTRY_LEN}, used: {len(value)})"
                )
            self._country = value.capitalize()
        else:
            self._country = value

    @property
    def city(self, ) -> str | None:
        return self._city

    @city.setter
    def city(self, value: str) -> None:
        if value is not None:
            if (len_city := len(value)) > self.MAX_COUNTRY_LEN:
                raise app.exceptions.IncorrectProfileValue(
                    f"The city name length is too long (Maximum is: "
                    f"{self.MAX_COUNTRY_LEN}, used: {len_city})"
                )
            self._city = value.capitalize()
        else:
            self._city = value

    @property
    def comment(self, ) -> str | None:
        return self._comment

    @comment.setter
    def comment(self, value: str) -> None:
        if value is not None and (len(value)) > self.MAX_COMMENT_LEN:
            raise app.exceptions.IncorrectProfileValue(
                f"The comment length is too long (Maximum is: "
                f"{self.MAX_COMMENT_LEN}, used: {len(value)})"
            )
        self._comment = value


class UserPropertiesProtocol(UserBasePropertiesProtocol, ):
    @property
    @abstractmethod
    def is_registered(self, ) -> bool:
        """Indicates whether the user is registered."""
        pass

    @is_registered.setter
    @abstractmethod
    def is_registered(self, value: bool) -> None:
        """Sets the registration status of the user."""
        pass

    @property
    @abstractmethod
    def connection(self, ) -> pg_ext_connection:
        """Provides the connection of the user."""
        pass

    @connection.setter
    @abstractmethod
    def connection(self, value: pg_ext_connection) -> None:
        """Sets the connection of the user."""
        pass


class UserDC(UserBaseDC, ):
    def __init__(
            self,
            tg_user_id: int,
            connection: pg_ext_connection | None = None,
            is_registered: bool | None = None,
            fullname: Optional[str] = None,
            goal: Optional[app.structures.base.Goal] = None,
            gender: Optional[app.structures.base.Gender] = None,
            age: Optional[int] = None,
            country: Optional[str] = None,
            city: Optional[str] = None,
            comment: Optional[str] = None,
            photos: Optional[list[str]] = None,
    ):
        super().__init__(
            fullname=fullname,
            goal=goal,
            gender=gender,
            age=age,
            country=country,
            city=city,
            comment=comment,
            photos=photos,
        )
        self.tg_user_id = tg_user_id
        self._connection = connection
        self._is_registered = is_registered


class UserProperties(UserDC, UserBaseProperties, UserPropertiesProtocol, ABC, ):
    CRUD: crud.users.User

    @property
    def is_registered(self, ) -> bool:
        if self._is_registered is None:
            self._is_registered: bool = bool(
                self.CRUD.db.read(
                    statement=self.CRUD.db.sqls.Users.IS_REGISTERED,
                    values=(self.tg_user_id,),
                    connection=self.connection
                ), )
        return self._is_registered

    @is_registered.setter
    def is_registered(self, value: bool, ) -> None:
        self._is_registered = value

    @property
    def connection(self, ) -> pg_ext_connection:
        self._connection: pg_ext_connection = self._connection or self.CRUD.db.get_user_connection()
        return self._connection

    @connection.setter
    def connection(self, value: pg_ext_connection, ) -> None:
        self._connection = value


class UserInterface(UserPropertiesProtocol, ABC, ):
    CRUD: crud.users.User

    @abstractmethod
    def __repr__(self, ) -> str:
        ...

    @abstractmethod
    def dict(self, ) -> app.structures.base.UserRaw:  # Make as property?  pragma: no cover. In use?
        ...

    @classmethod
    @abstractmethod
    def create(
            cls,
            user: User,
            fullname: str | None = None,
            goal: app.structures.base.Goal | None = None,
            gender: app.structures.base.Gender | None = None,
            age: int | None = None,
            country: str | None = None,
            city: str | None = None,
            comment: str | None = None,
    ) -> None:
        ...

    @classmethod
    @abstractmethod
    def read(cls, user: app.models.users.User, ) -> User | None:
        ...


class User(UserProperties, UserInterface, ):
    """Base User Logic across whole app (only logic actions)"""
    CRUD = crud.users.User

    def __repr__(self, ):  # pragma: no cover
        return repr(self._repr() | {'tg_user_id': self.tg_user_id})

    def dict(self, ):  # Make as property?  pragma: no cover. In use?
        # noinspection PyArgumentList
        return app.structures.base.UserRaw(
            tg_user_id=self.tg_user_id,
            fullname=self.fullname,
            goal=self.goal,
            gender=self.gender,
            age=self.age,
            city=self.city,
            country=self.country,
            comment=self.comment,
            photos=[photo for photo in self.photos],
        )

    @classmethod
    def create(
            cls,
            user: User,
            fullname: str | None = None,
            goal: app.structures.base.Goal | None = None,
            gender: app.structures.base.Gender | None = None,
            age: int | None = None,
            country: str | None = None,
            city: str | None = None,
            comment: str | None = None,
    ):
        cls.CRUD.create(
            tg_user_id=user.tg_user_id,
            fullname=fullname or user.fullname,
            goal=goal or user.goal,
            gender=gender or user.gender,
            age=age or user.age,
            country=country or user.country,
            city=city or user.city,
            comment=comment or user.comment,
            connection=user.connection,
        )

    @classmethod
    def read(cls, user: app.models.users.User, ) -> User | None:
        user_row: app.structures.base.ProfileDB = cls.CRUD.read(
            tg_user_id=user.tg_user_id,
            connection=user.connection,
        )
        return cls(tg_user_id=user.tg_user_id, **user_row, )  # Create one more user?

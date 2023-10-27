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
from typing import TYPE_CHECKING, Protocol, TypeAlias
from abc import ABC, abstractmethod

from app.utils import get_num_from_text
import app.exceptions
import app.constants
import app.models.base.users  # To inherit properties
import app.models.users
import app.models.matches
import app.models.mix  # To create photo

from app.models.matches import Matcher

if TYPE_CHECKING:
    pass

NewUserGoal: TypeAlias = app.models.users.User.Goal  # Just type for mypy
NewUserGender: TypeAlias = app.models.users.User.Gender  # Just type for mypy
FiltersGoal: TypeAlias = Matcher.Filters.Goal
FiltersGender: TypeAlias = Matcher.Filters.Gender
FiltersAge: TypeAlias = Matcher.Filters.Age


def shared_handle_goal(self: NewUserInterface | TargetInterface, text: str, ) -> None:
    """NewUser.handle_goal and TargetUser.handle_goal is identical for now, except self"""
    text = text.lower().strip()
    if not app.constants.Regexp.BACK_R.match(text) or self.back_btn_disabled:
        if text == app.constants.Search.Buttons.I_WANNA_CHAT.lower():
            self.goal = self.Goal.CHAT
        elif text == app.constants.Search.Buttons.I_WANNA_DATE.lower():
            self.goal = self.Goal.DATE
        elif text == app.constants.Search.Buttons.I_WANNA_CHAT_AND_DATE.lower():
            self.goal = self.Goal.BOTH
        else:
            raise app.exceptions.IncorrectProfileValue


class TargetProtocol(Protocol):
    """Instance attrs"""
    user: app.models.users.User
    goal: Matcher.Filters.Goal | None
    gender: Matcher.Filters.Gender | None
    age_range: tuple[int, int] | None
    country: str | None
    city: str | None
    filters: Matcher.Filters | None


class TargetInterface(ABC, TargetProtocol, ):

    class Mapper(ABC, ):
        Matcher: Matcher

    Goal: Matcher.Filters.Goal
    Gender: Matcher.Filters.Gender
    Age: Matcher.Filters.Age

    back_btn_disabled: bool

    @abstractmethod
    def handle_start_search(self, text: str, ):
        pass

    @abstractmethod
    def handle_goal(self, text: str, ):
        pass

    @abstractmethod
    def handle_gender(self, text: str, ):
        pass

    @abstractmethod
    def handle_age(self, text: str, ):
        pass

    @abstractmethod
    def handle_show_option(self, text: str, ):
        pass


class Target(TargetInterface, ):

    class Mapper:
        Matcher = Matcher

    Goal: FiltersGoal = Matcher.Filters.Goal
    Gender: FiltersGender = Matcher.Filters.Gender
    Age: FiltersAge = Matcher.Filters.Age

    back_btn_disabled: bool = True

    def __init__(
            self,
            user: app.models.users.User,
            goal: Goal | None = None,
            gender: Gender | None = None,
            age_range: tuple[int, int] | None = None,
            country: str | None = None,
            city: str | None = None,
            filters: Matcher.Filters | None = None,
    ):
        self.user = user
        self.goal = goal
        self.gender = gender
        self._age_range = age_range
        self.country = country
        self.city = city
        self.filters: Matcher.Filters = filters or self.Mapper.Matcher.Filters()

    def __repr__(self, ):
        d = {
            'self': object.__repr__(self, ),
            'goal': self.goal,
            'gender': self.gender,
            'age_range': self.age_range,
            'country': self.country,
            'city': self.city,
            'filters': self.filters,
        }
        return repr({k: v for k, v in d.items() if v is not None}) + '\n'

    @property  # Just to sort values, no validation
    def age_range(self, ) -> tuple[int, int] | None:
        return self._age_range

    @age_range.setter
    def age_range(self, value: tuple[int, int] | None, ) -> None:
        self._age_range = value
        if value is not None:
            # Mypy unable to detect that sorted(value) returns the same len as value
            self._age_range = tuple(sorted(value))  # type: ignore[assignment]

    @classmethod
    def get_age_from_text(cls, text: str, ) -> int | bool:
        try:
            num = get_num_from_text(text=text, )
            return num if cls.Age.MIN <= num <= cls.Age.MAX else False
        except ValueError:  # If unable convert str to int  TODO change error
            return False

    def handle_start_search(self, text: str, ) -> None:
        text = text.lower().strip()
        if not app.constants.Regexp.BACK_R.match(text) or self.back_btn_disabled:
            self.user.matcher.create_unfiltered_matches()
            if self.user.matcher.is_user_has_votes is False:
                raise app.exceptions.NoVotes
            elif self.user.matcher.is_user_has_covotes is False:
                raise app.exceptions.NoCovotes

    def handle_goal(self, text: str, ) -> None:
        """NewUser.handle_goal and TargetUser.handle_goal is identical for now, except self"""
        shared_handle_goal(self=self, text=text, )

    def handle_gender(self, text: str, ) -> None:
        text = text.lower().strip()
        if not app.constants.Regexp.BACK_R.match(text) or self.back_btn_disabled:
            if text == app.constants.Search.Buttons.MALE.lower():
                self.gender = self.Gender.MALE
            elif text == app.constants.Search.Buttons.FEMALE.lower():
                self.gender = self.Gender.FEMALE
            elif text == app.constants.Search.Buttons.ANY_GENDER.lower():
                self.gender = self.Gender.BOTH
            else:
                raise app.exceptions.IncorrectProfileValue

    def handle_age(self, text: str, ) -> None:
        text = text.lower().strip()
        if not app.constants.Regexp.BACK_R.match(text) or self.back_btn_disabled:
            if age := self.get_age_from_text(text=text, ):
                self.age_range = (age, age)
            elif all(
                    (  # Just as "and"
                            min_age := self.get_age_from_text(text=text[:2], ),
                            max_age := self.get_age_from_text(text=text[2:], )
                    )
            ):
                self.age_range = (min_age, max_age,)
            elif text == app.constants.Search.Buttons.ANY_AGE.lower():
                self.age_range = (self.Age.MIN, self.Age.MAX)
            else:
                raise app.exceptions.IncorrectProfileValue

    def handle_show_option(self, text: str, ) -> None:
        text = text.lower().strip()
        if not app.constants.Regexp.BACK_R.match(text) or self.back_btn_disabled:
            # Use startswith cuz text contain num of matches too
            if text.startswith(app.constants.Search.Buttons.SHOW_ALL.lower()):
                self.filters.match_type = self.filters.MatchType.ALL_MATCHES
            elif text.startswith(app.constants.Search.Buttons.SHOW_NEW.lower()):
                self.filters.match_type = self.filters.MatchType.NEW_MATCHES
            else:
                raise app.exceptions.IncorrectProfileValue
        self.user.matcher.set_current_matches()


class NewUserProtocol(Protocol, ):
    user: app.models.users.User
    fullname: str
    goal: Matcher.Filters.Goal
    gender: Matcher.Filters.Gender
    age: int | None
    country: str | None
    city: str | None
    comment: str | None
    photos: list[str]


class NewUserInterface(NewUserProtocol, ABC, ):
    class Mapper(ABC, ):
        Photo: app.models.mix.Photo

    Goal: app.structures.base.Goal
    Gender: app.models.users.User.Gender

    back_btn_disabled: bool

    @abstractmethod
    def _repr(self, ) -> dict:
        ...

    @abstractmethod
    def __repr__(self, ) -> str:
        ...

    @abstractmethod
    def handle_name(self, text: str, ) -> None:
        ...

    @abstractmethod
    def handle_goal(self, text: str, ) -> None:
        ...

    @abstractmethod
    def handle_gender(self, text: str, ) -> None:
        ...

    @abstractmethod
    def handle_age(self, text: str, ) -> None:
        ...

    @abstractmethod
    def handle_location_text(self, text: str, ) -> None:
        ...

    @abstractmethod
    def handle_comment(self, text: str, ) -> None:
        ...

    @abstractmethod
    def add_photo(self, photo: str, ) -> bool:  # Photo is really str?
        ...

    @abstractmethod
    def remove_photos(self, ) -> bool:
        ...

    @abstractmethod
    def create(self, ) -> None:
        ...


class NewUser(app.models.base.users.UserBaseProperties, NewUserInterface, ):
    """Base NewUser Logic across whole app. Should be inherited `for frameworks"""

    class Mapper:
        Photo: app.models.mix.Photo = app.models.mix.Photo

    Goal: NewUserGoal = app.models.users.User.Goal
    Gender: NewUserGender = app.models.users.User.Gender

    back_btn_disabled: bool = True

    def __init__(
            self,
            user: app.models.users.User,
            fullname: str | None = None,
            goal: Goal | None = None,
            gender: Gender | None = None,
            age: int | None = None,
            country: str | None = None,
            city: str | None = None,
            comment: str | None = None,
            photos: list[str] | None = None,
    ):
        super().__init__(
            fullname=fullname,
            goal=goal,
            gender=gender,
            age=age,
            country=country,
            city=city,
            comment=comment,
            photos=photos or [],
        )
        self.user: app.models.users.User = user

    def _repr(self, ) -> dict:
        return app.models.base.users.UserBaseProperties._repr(self=self, ) | {'tg_user_id': self.user.tg_user_id, }

    def __repr__(self, ) -> str:
        return repr(self._repr())

    def handle_name(self, text: str, ) -> None:
        if not app.constants.Regexp.BACK_R.match(text) or self.back_btn_disabled:
            self.fullname = text

    def handle_goal(self, text: str, ) -> None:
        """The same behavior as app.forms.user.Target.handle_goal. Dirty a bit"""
        text = text.lower().strip()
        shared_handle_goal(self=self, text=text, )

    def handle_gender(self, text: str, ) -> None:
        text = text.lower().strip()
        if not app.constants.Regexp.BACK_R.match(text) or self.back_btn_disabled:
            if text == app.constants.Reg.Buttons.I_MALE.lower():
                self.gender = self.Gender.MALE
            elif text == app.constants.Reg.Buttons.I_FEMALE.lower():
                self.gender = self.Gender.FEMALE
            else:
                raise app.exceptions.IncorrectProfileValue

    def handle_age(self, text: str, ) -> None:
        text = text.lower().strip()
        if not app.constants.Regexp.BACK_R.match(text) or self.back_btn_disabled:
            if app.constants.Regexp.SKIP_R.match(text):
                self.age = None  # Update if user set some value before
            elif age := ''.join([letter for letter in text if letter.isdigit()]):
                self.age = int(age)
            else:
                raise app.exceptions.IncorrectProfileValue

    def handle_location_text(self, text: str, ) -> None:
        text = text.strip()
        if not app.constants.Regexp.BACK_R.match(text) or self.back_btn_disabled:
            if app.constants.Regexp.SKIP_R.match(text):
                self.country = None
                self.city = None
            else:
                location = text.split(sep=',', maxsplit=1)
                self.country = location[0].strip()
                if len(location) > 1:  # If user specified a city too
                    self.city = location[1].strip()

    def handle_comment(self, text: str, ) -> None:
        text = text.strip()
        if not app.constants.Regexp.BACK_R.match(text) or self.back_btn_disabled:
            if app.constants.Regexp.SKIP_R.match(text):
                self.comment = None
            else:
                self.comment = text

    def add_photo(self, photo: str, ) -> bool:  # Photo is really str?
        if len(self.photos) < self.MAX_PHOTOS_COUNT:  # Don't use <= because post here post append
            self.photos.append(photo)
            return True
        return False

    def remove_photos(self, ) -> bool:
        if self.photos:
            self.photos.clear()
            return True
        else:
            return False

    def create(self, ) -> None:
        """... to distinct between unfilled value and intentionally filled with None value"""
        self.user.CRUD.upsert(
            tg_user_id=self.user.tg_user_id,
            fullname=self.fullname,
            goal=self.goal,
            gender=self.gender,
            age=self.age,
            country=self.country,
            city=self.city,
            comment=self.comment,
            connection=self.user.connection,
        )
        self.user.delete_photos()  # Delete old user_photos
        for photo in self.photos:
            self.Mapper.Photo.create(user=self.user, photo=photo, )
        self.user.is_registered = True

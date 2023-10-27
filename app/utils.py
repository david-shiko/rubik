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
from typing import TYPE_CHECKING, Type, Iterable

if TYPE_CHECKING:
    pass


class StringFormatDefaultDeprecated(str):
    """Implement str.format method with default value (the first passed param to format method"""

    def __init__(self, string: str, ):  # Don't use keyword style cuz it will be passed to __new__ and will fail
        self.original = string  # Regular string

    def format(self, *args, **kwargs) -> StringFormatDefaultDeprecated:
        formatted = self.original.format(*args, **kwargs)  # Regular string
        new_instance = type(self)(formatted, )  # Don't use keyword style cuz it will be passed to __new__ and will fail
        new_instance.original = self.original
        return new_instance


class StringFormatDefault(str):
    """Implement str.format method with default value (the first passed param to format method"""

    # Don't use keyword style cuz it will be passed to __new__ and will fail
    def __new__(cls, string: str, defaults: dict | Iterable, ) -> StringFormatDefault:
        if isinstance(defaults, dict, ):
            formatted_instance: StringFormatDefault = super().__new__(cls, string.format(**defaults), )
            formatted_instance.default_args = []
            formatted_instance.default_kwargs = defaults
        else:
            formatted_instance = super().__new__(cls, string.format(*defaults), )
            formatted_instance.default_args = defaults
            formatted_instance.default_kwargs = {}
        formatted_instance.original = string
        return formatted_instance

    def format(self: StringFormatDefault, *args, **kwargs) -> str:
        if self.default_args == args or self.default_kwargs == kwargs:
            return self
        return self.original.format(*(*self.default_args, *args, ), **{**self.default_kwargs, **kwargs, })


def get_num_from_text(text: str, ) -> int:
    num = int(''.join([letter for letter in text if letter.isdigit()]))
    return num


def limit_num(num: int, min_num: int, max_num: int, ) -> int:
    """Return num in given range or num limit"""
    num = min(max_num, max(min_num, num, ), )
    return num


def get_perc(num_1: int, num_2: int) -> int:
    """
    Get correlation (difference in percentage) of 2 numbers
    num_1 is smallest num
    num_2 is biggest num
    """
    if 0 in (num_1, num_2):
        return 0  # 0 from 100% == 100% from 0 == 0
    result = round((num_1 / num_2) * 100)  # Another analogue formulas: result = round(100 / (num_2 / num_1))
    return result


def raise_(e: Exception | Type[Exception]):
    # Move to method of error ?
    if isinstance(e, Exception):
        raise e
    raise e()

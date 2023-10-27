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

import gettext
import logging
from typing import Literal, Callable
from types import SimpleNamespace

import polib  # https://github.com/izimobil/polib/
from geopy.geocoders import Yandex  # For location
from apscheduler.schedulers.background import BackgroundScheduler

from app.config import YANDEX_API_KEY, LOG_ERROR_FILEPATH, LANGUAGE, LOCALES_PATH

locator = Yandex(api_key=YANDEX_API_KEY, timeout=3)  # for location


def create_basic_logger() -> logging.Logger:
    """Returned logger is the same every time (ROOT logger)"""
    # PTB will use logger of main file
    handler = logging.FileHandler(filename=LOG_ERROR_FILEPATH)
    handler.setLevel(logging.DEBUG)
    record_format = '[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
    logging.basicConfig(encoding='utf-8', format=record_format, level=logging.ERROR, handlers=[handler])
    return logging.getLogger()


def create_translations(
        filename: Literal['messages', 'reg', 'search', 'collections', 'posts', 'cmd_descriptions'],
) -> Callable:
    """Create translations for all strings but return translation only for one lang"""
    po = polib.pofile(pofile=f'{LOCALES_PATH}/{LANGUAGE}/LC_MESSAGES/{filename}.po', )
    po.save_as_mofile(fpath=f'{LOCALES_PATH}/{LANGUAGE}/LC_MESSAGES/{filename}.mo', )
    lang = gettext.translation(domain=filename, localedir=LOCALES_PATH, languages=[LANGUAGE, ])
    lang.install()
    return lang.gettext


def create_scheduler():
    background_scheduler = BackgroundScheduler()
    background_scheduler.start()
    return background_scheduler


translators = SimpleNamespace(
    messages=create_translations(filename='messages', ),
    reg=create_translations(filename='reg', ),
    search=create_translations(filename='search', ),
    collections=create_translations(filename='collections', ),
    posts=create_translations(filename='posts', ),
    cmd_descriptions=create_translations(filename='cmd_descriptions', ),
)

scheduler = create_scheduler()
logger = create_basic_logger()

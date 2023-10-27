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

from importlib import reload as importlib_reload  # To reload python loaded module
from pathlib import Path
from subprocess import run as subprocess_run
from typing import Callable

import pytest
from polib import pofile as polib_pofile

from app.postconfig import LOCALES_PATH, translators
from app import constants

lang_dirs = (directory.name for directory in Path(LOCALES_PATH).iterdir() if directory.is_dir())


def translator_decorator(func, translations: set, lang: str, attr_name: str, ):
    excluded = {"OK", }

    def wrapper(message: str, ):
        result = func(message=message, )
        if result == message and message not in excluded:
            raise Exception(
                f"Missing translation for string: {message}. Lang: {lang}, file: {attr_name}",  # pragma: no cover
            )
        translations.add(message, )
        return result

    return wrapper


@pytest.mark.parametrize(argnames="attr_name, gettext_func", argvalues=vars(translators).items(), )
@pytest.mark.parametrize(argnames="lang", argvalues=lang_dirs, )
def test_translations(attr_name: str, gettext_func: Callable, lang: str, ):
    used_msg_ids = set()
    po_file_path = f'{LOCALES_PATH}/{lang}/LC_MESSAGES/{attr_name}.po'
    setattr(
        translators, attr_name, translator_decorator(
            func=gettext_func,
            translations=used_msg_ids,
            lang=lang,
            attr_name=attr_name,
        ), )
    importlib_reload(constants, )  # Reload module with a decorated translators
    all_msg_ids = set(entry.msgid for entry in polib_pofile(po_file_path))  # All translations from  .po file
    # Check that all translations from file was used
    unused_translations = all_msg_ids - used_msg_ids
    error_str = (
        f'Not all translations were used in constants.\n'
        f'Lang: {lang}. File: "{attr_name}" Unused: {unused_translations}'
    )
    assert not unused_translations, error_str


@pytest.mark.parametrize(argnames="attr_name", argvalues=vars(translators).keys(), )
@pytest.mark.parametrize(argnames="lang", argvalues=lang_dirs, )
def test_msg_fmt(attr_name: str, lang: str, ):
    """Check errors with msgfmt utility"""
    po_file_path = f'{LOCALES_PATH}/{lang}/LC_MESSAGES/{attr_name}.po'
    subprocess_run(["msgfmt", "-c", po_file_path], check=True, capture_output=True, text=True, )

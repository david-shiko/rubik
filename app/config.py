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

from os import getenv as os_getenv
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

MAIN_ADMIN = 177381168
# @david_shiko, @david_neshiko, @Alex_vochis, @dubrovin_vladimir
ADMINS = [MAIN_ADMIN, 5064404775, 157218637, 790503987]
MAIN_ADMIN_NAME = '@david_shiko'

BOT_NAME = os_getenv('BOT_NAME', 838004799)  # Default prod
BOT_ID = os_getenv('BOT_ID', '@Rubik_Love_bot')  # Default prod
API_ID = os_getenv('API_ID')
API_HASH = os_getenv('API_HASH')
TG_BOT_TOKEN = os_getenv('TG_BOT_TOKEN')
YANDEX_API_KEY = os_getenv('YANDEX_API_KEY')
DB_PASSWORD = os_getenv('DB_PASSWORD')
LANGUAGE = os_getenv('LANGUAGE_', "en")  # Don't use "LANGUAGE" name cuz it's already used by unix system

# Use path because tg_fle_id correct only for bot chat
DEFAULT_PHOTO = os_getenv('DEFAULT_PHOTO_TG_FILE_ID', 'AgADAgADWqwxG2mlAAFIDtF_p9eVWNcS2bkPAAQBAAMCAAN4AAMKFQcAARYE')

DEBUG = os_getenv('DEBUG', 'False') == 'True'  # True only if 'True' passed

LOG_ERROR_FILENAME = 'error.log'
LOG_VIEW_FILENAME = 'views.log'
PROJECT_ROOT_PATH = Path(f'{Path(__file__).parent.parent}')
LOCALES_PATH = Path(__file__).parent / 'locales'
# Create parent dirs if not exists. parents - not create if not exists, exist_ok - not raise if exists
Path(f'{PROJECT_ROOT_PATH}/logs/').mkdir(parents=True, exist_ok=True)
LOG_ERROR_FILEPATH = Path(f'{PROJECT_ROOT_PATH}/logs/{LOG_ERROR_FILENAME}')
LOG_VIEW_FILEPATH = Path(f'{PROJECT_ROOT_PATH}/logs/{LOG_VIEW_FILENAME}')
Path(PROJECT_ROOT_PATH / 'db_backups/').mkdir(parents=True, exist_ok=True)


DEFAULT_POSTS = {  # Move to ptb config ?
    'EROTICA': {
        'Handcuffs_f': int(os_getenv('Handcuffs_f', False)) or None,
        'Public_nude_beach': int(os_getenv('Public_nude_beach', False)) or None,
        'BDSM_f': int(os_getenv('BDSM_f', False)) or None,
        'Strapon_m': int(os_getenv('Strapon_m', False)) or None,
        'Mistress': int(os_getenv('Mistress', False)) or None,
    },
    'MEMES': {
        'Rabbi': int(os_getenv('Rabbi', False)) or None,
        'Duck': int(os_getenv('Duck', False)) or None,
        'Superman': int(os_getenv('Superman', False)) or None,
        'Pixels': int(os_getenv('Pixels', False)) or None,
        'Dogs': int(os_getenv('Dogs', False)) or None,
    },
    'POEMS': {
        'We_are_alive_dog': int(os_getenv('We_are_alive_dog', False)) or None,
        'Echo_of_love': int(os_getenv('Echo_of_love', False)) or None,
        'Cliff': int(os_getenv('Cliff', False)) or None,
        'Like_that_you_not_sick_of_me': int(os_getenv('Like_that_you_not_sick_of_me', False)) or None,
        'Listen_filthy_heart': int(os_getenv('Listen_filthy_heart', False)) or None,
    },
    'ANIMALS': {
        'Yorkshire_Terrier': int(os_getenv('Yorkshire_Terrier', False, )) or None,
        'Maize_snake': int(os_getenv('Maize_snake', False, )) or None,
        'Domestic_rat': int(os_getenv('Domestic_rat', False, )) or None,
        'Cockatiel_parrot': int(os_getenv('Cockatiel_parrot', False, )) or None,
        'Bengal_cat': int(os_getenv('Bengal_cat', False, )) or None,
    },
    'FOOD': {
        'Dumplings': int(os_getenv('Dumplings', False, )) or None,
        'Onigiri': int(os_getenv('Onigiri', False, )) or None,
        'Pumpkin_soup': int(os_getenv('Pumpkin_soup', False, )) or None,
        'Pineapple_pizza': int(os_getenv('Pineapple_pizza', False, )) or None,
        'Sea_buckthorn_juice': int(os_getenv('Sea_buckthorn_juice', False, )) or None,
    },
    'FILMS': {
        'Gattaca': int(os_getenv('Gattaca', False, )) or None,
        'Who_Framed_Roger_Rabbit': int(os_getenv('Who_Framed_Roger_Rabbit', False, )) or None,
        'Avengers_Infinity_War': int(os_getenv('Avengers_Infinity_War', False, )) or None,
        'WATCH_OUT_FOR_THE_CAR': int(os_getenv('Watch_out_for_the_car', False, )) or None,
        'GIFTED': int(os_getenv('Gifted', False, )) or None,
    },
    'ART': {
        'Birth_of_venus': int(os_getenv('Birth_of_venus', False, )) or None,
        'Dog_biting_a_person_t': int(os_getenv('Dog_biting_a_person_t', False, )) or None,
        'Lost_in_Space': int(os_getenv('Lost_in_Space', False, )) or None,
        'Campbells_Soup_Cans': int(os_getenv('Campbells_Soup_Cans', False, )) or None,
        'Black_suprematist_square': int(os_getenv('Black_suprematist_square', False, )) or None,
    },
    'MUSIC': {
        'Smells_Like_Teen_Spirit': int(os_getenv('Smells_Like_Teen_Spirit', False, )) or None,
        'Despacito': int(os_getenv('Despacito', False, )) or None,
        'Roar': int(os_getenv('Roar', False, )) or None,
        'Chandelier': int(os_getenv('Chandelier', False, )) or None,
        'Another_one_bites_the_dust': int(os_getenv('Another_one_bites_the_dust', False, )) or None,
    },
    'PLACES': {
        'Monastery_of_Jeronimos': int(os_getenv('Monastery_of_Jeronimos', False, )) or None,
        'Eiffel_Tower': int(os_getenv('Eiffel_Tower', False, )) or None,
        'Zagut': int(os_getenv('Zagut', False, )) or None,
        'Strokkur': int(os_getenv('Strokkur', False, )) or None,
        'Vnukovo': int(os_getenv('Vnukovo', False, )) or None,
    },
    'PERSONS': {
        'Vasco_da_Gama': int(os_getenv('Vasco_da_Gama', False, )) or None,
        'Abraão_ben_Samuel_Zacuto': int(os_getenv('Abraão_ben_Samuel_Zacuto', False, )) or None,
        'Benjamin_Netanyahu': int(os_getenv('Benjamin_Netanyahu', False, )) or None,
        'Vladimir_Zhirinovsky': int(os_getenv('Vladimir_Zhirinovsky', False, )) or None,
        'Morgenshtern': int(os_getenv('Morgenshtern', False, )) or None,
    },
}

non_empty_default_posts: dict = {}
for collection_name, posts in DEFAULT_POSTS.items():
    if posts := {name: message_id for name, message_id in posts.items() if message_id is not None}:
        non_empty_default_posts[collection_name] = posts
DEFAULT_POSTS = non_empty_default_posts  # Remove None posts and collections

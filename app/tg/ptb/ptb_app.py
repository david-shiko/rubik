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
from typing import TYPE_CHECKING, Callable, Type

# noinspection PyPackageRequirements
from telegram.utils import request as tg_utils_request
# noinspection PyPackageRequirements
from telegram.ext import ExtBot, Updater, ContextTypes
# noinspection PyPackageRequirements
from telegram.error import BadRequest

from app.config import TG_BOT_TOKEN, PROJECT_ROOT_PATH, MAIN_ADMIN
from app.db import manager as db_manager

from custom_ptb.callback_context import CustomCallbackContext

from app.tg.ptb.structures import CustomUserData
from app.tg.classes.posts import PostsChannels
from app.tg.ptb import services
import app.tg.ptb.config
import app.tg.ptb.classes.posts
import app.forms.post
import app.tg.ptb.handlers_definition

if TYPE_CHECKING:
    from pathlib import PosixPath
    # noinspection PyPackageRequirements
    from telegram.ext import Handler
    # noinspection PyPackageRequirements
    from telegram import Bot

POSTS_PATH = PROJECT_ROOT_PATH / 'app' / 'assets' / 'default_posts'

PUBLIC_COLLECTIONS = PERSONAL_COLLECTIONS = {
    'PERSONS': [
        {
            'path': POSTS_PATH / 'persons' / 'Vladimir_Zhirinovsky' / 'Vladimir_Zhirinovsky',
            'text': 'Жириновский Владимир Вольфович (Эйдельштейн). Политический деятель. '
                    'Основатель и председатель Либерально-демократической партии России. 1946—2022.',
        },
        {
            'path': POSTS_PATH / 'persons' / 'Morgenshtern' / 'Morgenshtern',
            'text': 'Morgenshtern, Алише́р Таги́рович Моргенште́рн (Вале́ев). '
                    'Российский рэп- и поп-исполнитель, музыкант, шоумен.',
        },
        {
            'path': POSTS_PATH / 'persons' / 'Benjamin_Netanyahu' / 'Benjamin_Netanyahu',
            'text': 'Benjamin Netanyahu, - Бывший премьер-министр Израиля с 1996 по 1999 и с 2009 по 2021.',
        },
        {
            'path': POSTS_PATH / 'persons' / 'Abraão_ben_Samuel_Zacuto' / 'Abraão_ben_Samuel_Zacuto',
            'text': 'Abraão ben Samuel Zacuto, Астроном (1450-1515).',
        },
    ],
}


def check_is_bot_has_access_to_posts_store(bot: Bot, ) -> None:
    try:
        bot.get_chat(chat_id=PostsChannels.STORE.value, )
    except BadRequest:
        raise Exception('This bot has no access to posts channel store chat')
    return None


def read_and_upload_post_to_tg_server(bot: ExtBot, post: dict[str, PosixPath | str], ):
    with open(post['path'], 'rb') as f:
        sent_message = bot.send_photo(  # Use another method to send video, music, etc
            chat_id=PostsChannels.STORE.value,
            photo=f.read(),
            caption=post['text'],
        )
        return sent_message


def create_default_collections_with_posts(
        bot: Bot,
        collections: dict[str, list[dict[str, PosixPath | str]]],
        post_cls: Type[app.forms.post.PublicPostInterface | app.forms.post.PersonalPostInterface],
):
    if post_cls == app.forms.post.PublicPost:
        prefix = services.Collection.NamePrefix.PUBLIC
    else:
        prefix = services.Collection.NamePrefix.PERSONAL

    already_created_collections = services.Collection.get_defaults_names(prefix=prefix, )
    required_collection_names = set(collections) - set(already_created_collections)
    for name in required_collection_names:
        created_collection_posts = []
        for post_source in collections[name]:
            sent_message = read_and_upload_post_to_tg_server(bot=bot, post=post_source, )
            post = post_cls(author=services.System.user, message_id=sent_message.message_id, )
            created_collection_posts.append(post.create())
        services.System.set_bots_votes_to_posts(posts=created_collection_posts, )
        services.Collection.create_default(
            name=name,
            posts=created_collection_posts,
            prefix=prefix,
        )


def create_bots_default_photos(bot: ExtBot, filename_prefix: str | None = None, ):
    result = []
    for filename_gender_prefix in ('m', 'w'):  # 'w' - woman, 'm' - man (May be obsolete)
        for i in range(1, 6):
            filename = filename_prefix or f'{filename_gender_prefix}{i}'
            photo_path = str(PROJECT_ROOT_PATH / 'app' / 'assets' / 'photos' / filename)
            with open(photo_path, 'rb') as photo_file:
                message = bot.send_photo(chat_id=MAIN_ADMIN, photo=photo_file, )
                file_id = message.photo[-1].file_id
                result.append(file_id)
    print(result)  # PArt of logic


def create_ptb_bot() -> ExtBot:
    ext_bot = ExtBot(token=TG_BOT_TOKEN, request=tg_utils_request.Request(con_pool_size=16), )
    return ext_bot


def create_ptb_app(
        bot: ExtBot,
        handlers: list[dict[str, Handler]] | None = None,
        error_handlers: list[dict[str, Callable]] | None = None,
):
    updater = Updater(
        bot=bot,
        context_types=ContextTypes(
            context=CustomCallbackContext,
            user_data=CustomUserData,
        )
    )
    if handlers is None:
        handlers = app.tg.ptb.handlers_definition.get_regular_handlers() + app.tg.ptb.handlers_definition.get_chs()
    if error_handlers is None:
        error_handlers = app.tg.ptb.handlers_definition.get_error_handlers()
    app.tg.ptb.handlers_definition.set_handlers(
        dispatcher=updater.dispatcher,
        handlers=handlers,
        error_handlers=error_handlers,
    )
    return updater


def configure_app(
        config: app.tg.ptb.config.Config,
        create_public_default_collections: bool = True,
        create_personal_default_collections: bool = True,
) -> None:  # Pass the class directly?
    """Will change passed config"""
    for key, value in vars(config).items():
        setattr(app.tg.ptb.config.Config, key, value)
    db_manager.Postgres.create_app_tables()
    check_is_bot_has_access_to_posts_store(bot=config.bot, )
    if create_public_default_collections is True:
        create_default_collections_with_posts(
            bot=config.bot,
            collections=PUBLIC_COLLECTIONS,
            # Need app forms layer cuz, ptb layer will fail on resend attempt
            post_cls=app.forms.post.PublicPost,
        )
    if create_personal_default_collections is True:
        create_default_collections_with_posts(
            bot=config.bot,
            collections=PERSONAL_COLLECTIONS,
            # Need app forms layer cuz, ptb layer will fail on resend attempt
            post_cls=app.forms.post.PersonalPost,
        )


def start_ptb_bot(updater: Updater, idle: bool = True, ):
    """Infinite blocking func (updater.start_polling)"""
    print(updater.bot.get_me())
    updater.start_polling()
    updater.idle() if idle else None  # Running idle will block a next execution, idle is a blocking function.

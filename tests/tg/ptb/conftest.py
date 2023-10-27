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
from typing import TYPE_CHECKING
from unittest.mock import create_autospec, patch
import datetime

from pytest import fixture

# noinspection PyPackageRequirements
from telegram import (
    Update as tg_Update,
    Chat as tg_Chat,
    User as tg_ptb_User,
    Message as tg_Message,
    CallbackQuery as tg_CallbackQuery,
    Contact as tg_Contact,
    Location,
    PhotoSize as tg_PhotoSize,
    UserProfilePhotos as tg_UserProfilePhotos,
)
# noinspection PyUnresolvedReferences,PyPackageRequirements
from telegram.ext import (
    Defaults as tg_Defaults,
    ExtBot,
)
# noinspection PyPackageRequirements
from telegram.error import BadRequest as tg_error_BadRequest

import app.postconfig  # To create mock spec

import app.tg.ptb.ptb_app
import app.tg.ptb.config
import app.tg.ptb.views
import app.tg.ptb.actions

import app.tg.ptb.classes.collections
import app.tg.ptb.classes.users
import app.tg.ptb.classes.votes
import app.tg.ptb.classes.matches
import app.tg.ptb.forms.user
import app.tg.ptb.forms.post

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    # noinspection PyUnresolvedReferences,PyPackageRequirements
    from telegram.ext import ExtBot as tg_ExtBot
    import app.structures.base
    from app.models import mix
    import app.models.users
    import app.models.posts
    import app.models.votes
    import app.forms.user


def get_user_profile_photos() -> tg_UserProfilePhotos:
    return tg_UserProfilePhotos(
        total_count=2,
        photos=[  # It's 2 photos, not 8
            [tg_PhotoSize(file_id='1', file_unique_id='1', width=10, height=10),
             tg_PhotoSize(file_id='2', file_unique_id='2', width=20, height=20),
             tg_PhotoSize(file_id='1', file_unique_id='1', width=10, height=10),
             tg_PhotoSize(file_id='2', file_unique_id='2', width=20, height=20), ],
            [tg_PhotoSize(file_id='1', file_unique_id='1', width=10, height=10),
             tg_PhotoSize(file_id='2', file_unique_id='2', width=20, height=20),
             tg_PhotoSize(file_id='1', file_unique_id='1', width=10, height=10),
             tg_PhotoSize(file_id='2', file_unique_id='2', width=20, height=20), ],
        ]
    )


@fixture(scope='session')
def tg_ptb_photo_s() -> list[tg_PhotoSize]:
    """tg_photo (message.photo) represents list of photos with different sizes (the last one is the best quality)"""
    yield get_user_profile_photos().photos[-1]


@fixture(scope='session', )
def ptb_app_config(mock_ptb_bot_s: MagicMock, ) -> app.tg.ptb.config.Config:
    yield app.tg.ptb.config.Config(
        bot=mock_ptb_bot_s,
        logger=create_autospec(spec=app.postconfig.logger, spec_set=True, ),
        sleep_function=create_autospec(spec=callable, spec_set=True, ),
        is_log=False,
    )


@fixture(scope='session', autouse=True, )
def configure_app(ptb_app_config: app.tg.ptb.config.Config, ) -> None:
    """Will override global config"""
    app.tg.ptb.ptb_app.configure_app(  # No need to create default collections and posts (causing check error)
        config=ptb_app_config,
        create_public_default_collections=False,
        create_personal_default_collections=False,
    )


def get_tg_callback_query(
        tg_ptb_user_s: tg_ptb_User,
        chat_instance: str,
        message: tg_Message,
        bot: tg_ExtBot,
        callback_id: str,
) -> tg_CallbackQuery:
    return tg_CallbackQuery(
        id=callback_id,
        from_user=tg_ptb_user_s,
        chat_instance=chat_instance,
        message=message,
        bot=bot,
    )


@fixture(scope='function')
def tg_callback_query_f(
        tg_ptb_user_s: tg_ptb_User,
        tg_message_s: tg_Message,
        tg_chat_s: tg_Chat,
        mock_ptb_bot: MagicMock,
) -> tg_CallbackQuery:
    yield get_tg_callback_query(
        callback_id='1',
        tg_ptb_user_s=tg_ptb_user_s,
        chat_instance=tg_chat_s.type,
        message=tg_message_s,
        bot=mock_ptb_bot,  # Bot need for cbk.answer
    )


@fixture(scope='session')
def tg_callback_query_s(
        tg_ptb_user_s: tg_ptb_User,
        tg_message_s: tg_Message,
        tg_chat_s: tg_Chat,
        mock_ptb_bot_s: MagicMock,
) -> tg_CallbackQuery:
    yield get_tg_callback_query(
        callback_id='1',
        tg_ptb_user_s=tg_ptb_user_s,
        chat_instance=tg_chat_s.type,
        message=tg_message_s,
        bot=mock_ptb_bot_s,
    )


def get_tg_chat(tg_ptb_user_s: tg_ptb_User = None) -> tg_Chat:
    return tg_Chat(id=tg_ptb_user_s.id, type='private', username=tg_ptb_user_s.username, )


@fixture(scope='session')
def tg_chat_s(tg_ptb_user_s: tg_ptb_User):
    yield get_tg_chat(tg_ptb_user_s=tg_ptb_user_s, )


@fixture(scope='session')
def tg_contact_s(tg_ptb_user_s: tg_ptb_User):
    yield tg_Contact(phone_number='+123456', first_name=tg_ptb_user_s.first_name, user_id=tg_ptb_user_s.id, )


def get_tg_message(
        tg_ptb_user_s: tg_ptb_User,
        tg_chat: tg_Chat,
        date: datetime.datetime,
        message_id: int = 1,
        *args,
        **kwargs,
) -> tg_Message:
    result = tg_Message(
        from_user=tg_ptb_user_s,
        message_id=message_id,
        chat=tg_chat,
        date=date,
        *args,
        **kwargs,
    )
    return result


@fixture(scope='session')
def tg_message_s(
        tg_ptb_user_s: tg_ptb_User,
        tg_chat_s: tg_Chat,
        frozen_datetime: datetime.datetime,
) -> tg_Message:
    # User "get_tg_message" because message need to dependency (mock_bot), direct usage will cause an infinite loop
    message = get_tg_message(tg_ptb_user_s=tg_ptb_user_s, tg_chat=tg_chat_s, date=frozen_datetime, )
    yield message


@fixture(scope='function')
def tg_message_f(
        tg_ptb_user_s: tg_ptb_User,
        tg_chat_s: tg_Chat,
        frozen_datetime: datetime.datetime,
        mock_ptb_bot_s: MagicMock,
) -> tg_Message:
    message = get_tg_message(tg_ptb_user_s=tg_ptb_user_s, tg_chat=tg_chat_s, date=frozen_datetime, bot=mock_ptb_bot_s, )
    yield message


@fixture(scope='function')
def mock_tg_message(tg_message_s: tg_Message) -> MagicMock:
    message = create_autospec(spec=tg_message_s, spec_set=True, )
    yield message


def get_tg_ptb_user(user_config: app.structures.base.UserRaw, ):
    # In telegram username are with (@ and underscore), full_name are with space
    first_name, last_name = user_config['fullname'].split(' ')
    return tg_ptb_User(
        id=user_config['tg_user_id'],
        # Telegram username is without "@" sign unlike "user.tg_name"
        username=user_config['fullname'].replace(' ', '_'),
        first_name=first_name,
        last_name=last_name,
        is_bot=False,
    )


@fixture(scope='session')
def tg_ptb_user_s(user_config: app.structures.base.UserRaw, ) -> tg_ptb_User:
    """In telegram username are with underscore, full_name are with space"""
    yield get_tg_ptb_user(user_config=user_config, )


@fixture(scope='function')
def tg_ptb_user_f(user_config: app.structures.base.UserRaw, ) -> tg_ptb_User:
    """In telegram username are with underscore, full_name are with space"""
    yield get_tg_ptb_user(user_config=user_config, )


def get_tg_update(
        callback_query: tg_CallbackQuery,
        message: tg_Message,
        update_id: int,
        *args,
        **kwargs,
) -> tg_Update:
    """
    Order of building update: bot + user_config -> tg_user -> tg_chat -> tg_message + tg_callback -> tg_update
    """
    return tg_Update(
        update_id=update_id,
        message=message,
        callback_query=callback_query,
        *args,
        **kwargs,
    )


@fixture(scope='function')
def tg_update_f(
        mock_ptb_bot_s: MagicMock,
        tg_message_f: tg_Message,
        tg_callback_query_f: tg_CallbackQuery,
) -> tg_Update:
    tg_update = get_tg_update(
        update_id=1,
        message=tg_message_f,
        callback_query=tg_callback_query_f,
    )
    yield tg_update


@fixture(scope='session')
def tg_update_s(tg_message_s: tg_Message, tg_callback_query_s: tg_CallbackQuery, ) -> tg_Update:
    tg_update = get_tg_update(
        update_id=1,
        message=tg_message_s,
        callback_query=tg_callback_query_s,
    )
    yield tg_update


@fixture(scope='function')
def mock_tg_update_f(tg_update_f: tg_Update, ) -> MagicMock:
    mock_update = create_autospec(spec=tg_update_f, spec_set=True, )
    yield mock_update


@fixture(scope='session')
def ptb_bot_s() -> ExtBot:
    ext_bot = ExtBot(token='123:4:5', )  # Exactly such fake token to bypass token pre-validation
    ext_bot._bot = {  # Hardcoded; Assign manually to avoid api call
        'can_join_groups': False,
        'can_read_all_group_messages': False,
        'first_name': 'Rubik love bot locale',
        'id': 5729287192,
        'is_bot': True,
        'supports_inline_queries': False,
        'username': 'RubikLoveLocalBot',
    }
    ext_bot._commands = []  # In reality filled with telegram.botcommand.BotCommand; Assign manually to avoid api call
    yield ext_bot


def get_mock_ptb_bot(bot: ExtBot, ) -> MagicMock:
    def side_effect_deco(func: MagicMock):
        def deco(chat_id: int | str, *_, **__, ):
            if int(chat_id) == -1:  # Raise if negative
                raise tg_error_BadRequest(message='')
            return func.return_value

        return deco

    mock_ext_bot = create_autospec(spec=bot, spec_set=True, )
    mock_ext_bot.defaults = tg_Defaults(run_async=False)  # Some internal real bot config
    mock_ext_bot.get_chat.side_effect = side_effect_deco(func=mock_ext_bot.get_chat)  # The same side_effect
    mock_ext_bot.delete_message.side_effect = side_effect_deco(func=mock_ext_bot.delete_message)  # The same side_effect
    mock_ext_bot.request.con_pool_size = 16
    return mock_ext_bot


@fixture(scope='session')
def mock_ptb_bot_s(ptb_bot_s: ExtBot, ) -> MagicMock:
    yield get_mock_ptb_bot(bot=ptb_bot_s, )


@fixture(scope='function')
def mock_ptb_bot(ptb_bot_s: ExtBot, ) -> MagicMock:
    yield get_mock_ptb_bot(bot=ptb_bot_s, )


@fixture(scope='function', )
def ptb_user_f(user_f: app.models.users.User, ) -> app.tg.ptb.classes.users.User:
    tg_user = app.tg.ptb.classes.users.User.from_user(user=user_f, )
    tg_user.tg_name = '@firstname lastname'
    yield tg_user


@fixture(scope='session', )
def ptb_user_s(user_s: app.models.users.User, ) -> app.tg.ptb.classes.users.User:
    tg_user = app.tg.ptb.classes.users.User.from_user(user=user_s, )
    tg_user.tg_name = '@firstname lastname'
    yield tg_user


@fixture(scope='session', )
def ptb_user_s2(user_s2: app.models.users.User, ) -> app.tg.ptb.classes.users.User:
    tg_user = app.tg.ptb.classes.users.User.from_user(user=user_s2, )
    tg_user.tg_name = '@firstname2 lastname2'
    yield tg_user


@fixture(scope='function', )
def ptb_profile_f(ptb_user_f: app.tg.ptb.classes.users.User, ) -> app.tg.ptb.classes.users.Profile:
    yield app.tg.ptb.classes.users.Profile(user=ptb_user_f, )


@fixture(scope='session', )
def ptb_profile_s(ptb_user_s: app.tg.ptb.classes.users.User, ) -> app.tg.ptb.classes.users.Profile:
    yield app.tg.ptb.classes.users.Profile(user=ptb_user_s)


@fixture(scope='function', )
def mock_ptb_profile(ptb_profile_f: app.tg.ptb.classes.users.Profile, ) -> MagicMock:
    yield create_autospec(spec=ptb_profile_f, spec_set=True, )


@fixture(scope='function', )
def mock_ptb_matcher(ptb_user_s: app.tg.ptb.classes.users.User, ) -> MagicMock:
    yield create_autospec(spec=ptb_user_s.matcher, spec_set=True, )


@fixture(scope='session', )
def tg_ptb_match_s(
        match_s: app.models.matches.Match,
        ptb_user_s: app.tg.ptb.classes.users.UserInterface,
        ptb_user_s2: app.tg.ptb.classes.users.UserInterface,
) -> app.tg.ptb.classes.matches.Match:
    match = app.tg.ptb.classes.matches.Match(
        id=match_s.id,
        owner=ptb_user_s,
        user=ptb_user_s2,
        common_posts_perc=match_s.stats.common_posts_perc,
        common_posts_count=match_s.stats.common_posts_count,
    )
    yield match


@fixture(scope='function', )
def mock_tg_ptb_match(tg_ptb_match_s: app.tg.ptb.classes.matches.Match, ) -> MagicMock:
    yield create_autospec(spec=tg_ptb_match_s, spec_set=True, )


@fixture(scope='function', )
def mock_ptb_user(
        ptb_user_s: app.tg.ptb.classes.users.User,
        collection: app.models.collections.Collection,
) -> MagicMock:
    mock_ptb_user = create_autospec(spec=ptb_user_s, collections=[], connection=ptb_user_s.connection, spec_set=True, )
    mock_ptb_user.get_collections.return_value = [collection]  # Not all collections
    mock_ptb_user.matcher.is_user_has_covotes = False
    yield mock_ptb_user


@fixture(scope='session', )  # Rename me
def mock_ptb_user_s(
        ptb_user_s: app.tg.ptb.classes.users.User, collection: app.models.collections.Collection, ) -> MagicMock:
    mock_ptb_user = create_autospec(spec=ptb_user_s, collections=[], connection=ptb_user_s.connection, spec_set=True, )
    mock_ptb_user.matcher.is_user_has_covotes = False
    yield mock_ptb_user


@fixture(scope='function', )
def ptb_new_user_f(
        new_user_f: app.forms.user.NewUser,
) -> app.tg.ptb.forms.user.NewUser:
    yield app.tg.ptb.forms.user.NewUser(
        fullname=new_user_f.fullname,
        goal=new_user_f.goal,
        gender=new_user_f.gender,
        age=new_user_f.age,
        country=new_user_f.country,
        city=new_user_f.city,
        comment=new_user_f.comment,
        photos=new_user_f.photos,
        user=new_user_f.user,
    )


@fixture(scope='function', )
def mock_ptb_new_user_f(
        ptb_new_user_f: app.tg.ptb.forms.user.NewUser,
) -> MagicMock:
    yield create_autospec(spec=ptb_new_user_f, spec_set=True, )


@fixture(scope='function', )
def mock_ptb_public_post_form(ptb_user_f: app.tg.ptb.classes.users.User, ) -> MagicMock:
    post_form = app.tg.ptb.forms.post.PublicPost(author=ptb_user_f, message_id=2, )
    mock_post_form = create_autospec(spec=post_form, spec_set=True, )
    yield mock_post_form


@fixture(scope='session', )
def ptb_public_post_s(public_post_s: app.models.posts.PublicPost, ) -> app.tg.ptb.classes.posts.PublicPost:
    post = app.tg.ptb.classes.posts.PublicPost(
        author=public_post_s.author,
        post_id=public_post_s.post_id,
        message_id=1,
    )
    yield post


@fixture(scope='function', )
def mock_ptb_public_post(ptb_public_post_s: app.tg.ptb.classes.posts.PublicPost, ) -> MagicMock:
    mock_post = create_autospec(spec=ptb_public_post_s, spec_set=True, )
    yield mock_post


@fixture(scope='function', )
def mock_ptb_personal_post_form(ptb_user_f: app.tg.ptb.classes.users.User, ) -> MagicMock:
    post_form = app.tg.ptb.forms.post.PersonalPost(
        author=ptb_user_f,
        message_id=1,
    )
    mock_sample = create_autospec(spec=post_form, spec_set=True, )
    yield mock_sample


@fixture(scope='session', )
def tg_ptb_voted_public_post(
        ptb_public_post_s: app.tg.ptb.classes.posts.PersonalPost,
        ptb_public_vote_s: app.tg.ptb.classes.votes.PersonalVote
) -> app.tg.ptb.classes.posts.VotedPublicPostInterface:
    return app.tg.ptb.classes.posts.VotedPublicPost(
        post=ptb_public_post_s,
        clicker_vote=ptb_public_vote_s,
    )


@fixture(scope='function', )
def mock_tg_ptb_voted_public_post(
        tg_ptb_voted_public_post: app.tg.ptb.classes.posts.VotedPublicPostInterface,
) -> MagicMock:
    yield create_autospec(spec=tg_ptb_voted_public_post, spec_set=True, )


@fixture(scope='function', )
def tg_ptb_channel_public_post_f(
        ptb_public_post_s: app.tg.ptb.classes.posts.PublicPost,
) -> app.tg.ptb.classes.posts.ChannelPublicPost:
    post = app.tg.ptb.classes.posts.ChannelPublicPost(**vars(ptb_public_post_s))
    yield post


@fixture(scope='function', )
def mock_tg_ptb_channel_public_post(
        tg_ptb_channel_public_post_f: app.tg.ptb.classes.posts.ChannelPublicPost, ) -> MagicMock:
    mock_post = create_autospec(spec=tg_ptb_channel_public_post_f, spec_set=True, )
    yield mock_post


@fixture(scope='session', )
def ptb_personal_post_s(personal_post_s: app.models.posts.PersonalPost, ) -> app.tg.ptb.classes.posts.PersonalPost:
    post = app.tg.ptb.classes.posts.PersonalPost(
        author=personal_post_s.author,
        post_id=personal_post_s.post_id,
        message_id=1,
    )
    yield post


@fixture(scope='function', )
def mock_ptb_personal_post(ptb_personal_post_s: app.tg.ptb.classes.posts.PersonalPost) -> MagicMock:
    mock_post = create_autospec(spec=ptb_personal_post_s, spec_set=True, )
    yield mock_post


@fixture(scope='function', )
def mock_ptb_personal_post_form(ptb_user_f: app.tg.ptb.classes.users.User, ) -> MagicMock:
    post_form = app.tg.ptb.forms.post.PersonalPost(
        author=ptb_user_f,
        message_id=1,
    )
    mock_sample = create_autospec(spec=post_form, spec_set=True, )
    yield mock_sample


@fixture(scope='session', )
def tg_ptb_voted_personal_post(
        ptb_personal_post_s: app.tg.ptb.classes.posts.PersonalPost,
        ptb_personal_vote_s: app.tg.ptb.classes.votes.PersonalVote
) -> app.tg.ptb.classes.posts.VotedPersonalPost:
    return app.tg.ptb.classes.posts.VotedPersonalPost(
        post=ptb_personal_post_s,
        clicker_vote=ptb_personal_vote_s,
        opposite_vote=ptb_personal_vote_s,
    )


@fixture(scope='function', )
def mock_tg_ptb_voted_personal_post(
        tg_ptb_voted_personal_post: app.tg.ptb.classes.posts.VotedPersonalPost, ) -> MagicMock:
    yield create_autospec(spec=tg_ptb_voted_personal_post, spec_set=True, )


# @fixture(scope='session', )
# def tg_location() -> Location:
#     location = Location(45, 45, )
#     yield location


@fixture(scope='session')
def ptb_public_vote_s(
        public_vote_s: app.models.votes.PublicVote,
        ptb_user_s: app.tg.ptb.classes.users.User,
) -> app.tg.ptb.classes.votes.PublicVote:
    yield app.tg.ptb.classes.votes.PublicVote(
        user=ptb_user_s,
        post_id=public_vote_s.post_id,
        message_id=public_vote_s.message_id,
        value=public_vote_s.value,
    )


@fixture(scope='session')
def ptb_personal_vote_s(
        personal_vote_s: app.models.votes.PersonalVote,
        ptb_user_s: app.tg.ptb.classes.users.User,
) -> app.tg.ptb.classes.votes.PersonalVote:
    yield app.tg.ptb.classes.votes.PersonalVote(
        user=ptb_user_s,
        post_id=personal_vote_s.post_id,
        message_id=personal_vote_s.message_id,
        value=personal_vote_s.value,
    )


@fixture(scope='session')
def ptb_collection_s(ptb_user_s: app.tg.ptb.classes.users.User, ) -> app.tg.ptb.classes.collections.Collection:
    collection = app.tg.ptb.classes.collections.Collection(author=ptb_user_s, collection_id=1, )
    yield collection


@fixture(scope='function')
def mock_ptb_collection(ptb_collection_s: app.tg.ptb.classes.collections.Collection, ) -> MagicMock:
    mock_collection = create_autospec(spec=ptb_collection_s, spec_set=True, )
    yield mock_collection


def get_mock_tg_view(ptb_user: app.tg.ptb.classes.users.User, bot: ExtBot, ) -> MagicMock:
    view = app.tg.ptb.views.View(user=ptb_user, bot=bot, )
    mock_view = create_autospec(spec=view, spec_set=True, )
    return mock_view


@fixture(scope='session')  # Session because used in mock_context (which need to preserve states inside CH)
def mock_tg_view_s(ptb_user_s: app.tg.ptb.classes.users.User, ptb_bot_s: ExtBot, ) -> MagicMock:
    yield get_mock_tg_view(ptb_user=ptb_user_s, bot=ptb_bot_s, )


@fixture(scope='function')
def mock_tg_view_f(ptb_user_f: app.tg.ptb.classes.users.User, ptb_bot_s: ExtBot, ) -> MagicMock:
    yield get_mock_tg_view(ptb_user=ptb_user_f, bot=ptb_bot_s, )


@fixture(scope='session')
def ptb_target_s(target_s: app.forms.user.Target, ) -> app.tg.ptb.forms.user.Target:
    yield app.tg.ptb.forms.user.Target(**(vars(target_s) | {'age_range': vars(target_s).pop('_age_range')}))


@fixture(scope='function')
def mock_ptb_target(ptb_target_s: app.tg.ptb.forms.user.Target, ) -> MagicMock:
    mock_ptb_target = create_autospec(spec=ptb_target_s, spec_set=True, )
    yield mock_ptb_target


@fixture(scope='function', )
def bot_public_post_s(
        ptb_public_post_s: app.tg.ptb.classes.posts.PublicPost,
) -> app.tg.ptb.classes.posts.BotPublicPost:
    yield app.tg.ptb.classes.posts.BotPublicPost(**vars(ptb_public_post_s), )


@fixture(scope='function', )
def mock_ptb_bot_public_post(bot_public_post_s: app.tg.ptb.classes.posts.BotPublicPost, ) -> MagicMock:
    yield create_autospec(spec=bot_public_post_s, spec_set=True, )


@fixture(scope='function')
def mock_ptb_match_stats(ptb_user_s: app.tg.ptb.classes.users.User, ) -> MagicMock:
    spec = app.tg.ptb.classes.matches.MatchStats(
        user=ptb_user_s,
        with_tg_user_id=2,
        set_statistic=False,
    )
    result = create_autospec(spec=spec, spec_set=True, )
    yield result


# # # PATCHED # # #

@fixture(scope='function', )
def patched_actions() -> MagicMock:
    """patch_actions_module"""
    with patch.object(app.tg.ptb, 'actions', autospec=True, ) as mock_actions:
        mock_actions.check_correct_continue.return_value = False
        mock_actions.check_is_collections_chosen.return_value = False
        mock_actions.accept_user_handler.return_value = False
        yield mock_actions


@fixture(scope='function')
def patched_ptb_bot(mock_ptb_bot_s: MagicMock, ):
    assert mock_ptb_bot_s == app.tg.ptb.config.Config.bot  # Already mocked by configure_app
    mock_ptb_bot_s.reset_mock()
    yield mock_ptb_bot_s


@fixture(scope='function')  # Will patch during all the test
def patched_logger() -> MagicMock:
    # If already patched. NonCallableMagicMock - result of "create_autospec"
    app.tg.ptb.config.Config.logger.reset_mock()
    yield app.tg.ptb.config.Config.logger


@fixture(scope='function', )  # Will patch for entire scope (module) were was called
def patched_ptb_public_post() -> MagicMock:
    mock_post = create_autospec(spec=app.tg.ptb.classes.posts.PublicPost, spec_set=True, )
    with patch.object(app.tg.ptb.classes.posts, 'PublicPost', mock_post, ):
        yield mock_post


@fixture(scope='function', )  # Will patch for entire scope (module) were was called
def patched_ptb_channel_public_post() -> MagicMock:
    mock_post = create_autospec(spec=app.tg.ptb.classes.posts.ChannelPublicPost, spec_set=True, )
    with patch.object(app.tg.ptb.classes.posts, 'ChannelPublicPost', mock_post, ):
        yield mock_post


@fixture(scope='function', )
def patched_ptb_personal_post(mock_ptb_user: MagicMock, ) -> MagicMock:
    mock_post_cls = create_autospec(spec=app.tg.ptb.classes.posts.PersonalPost, spec_set=True, )
    with patch.object(app.tg.ptb.classes.posts, 'PersonalPost', mock_post_cls, ):
        # mock_post_cls.extract_cbk_data.return_value = [mock_ptb_user_s, None, ]
        yield mock_post_cls


@fixture(scope='function', )
def patched_ptb_public_vote(
        mock_ptb_user: app.tg.ptb.classes.users.User,
) -> MagicMock:
    mock_vote_cls = create_autospec(spec=app.tg.ptb.classes.votes.PublicVote, spec_set=True, )
    with patch.object(app.tg.ptb.classes.votes, 'PublicVote', mock_vote_cls, ):
        # mock_post_cls.extract_cbk_data.return_value = [mock_ptb_user_s, None, ]
        yield mock_vote_cls


@fixture(scope='function', )
def patched_ptb_personal_vote(mock_ptb_user: MagicMock, ) -> MagicMock:
    mock_vote_cls = create_autospec(spec=app.tg.ptb.classes.votes.PersonalVote, spec_set=True, )
    with patch.object(app.tg.ptb.classes.votes, 'PersonalVote', mock_vote_cls, ):
        # mock_post_cls.extract_cbk_data.return_value = [mock_ptb_user_s, None, ]
        yield mock_vote_cls


@fixture(scope='function')  # Will patch during all the test
def patched_ptb_collection() -> MagicMock:
    with patch.object(app.tg.ptb.classes.collections, 'Collection', autospec=True, ) as m:
        yield m


@fixture(scope='function')  # Will patch during all the test
def patched_ptb_post_base() -> MagicMock:
    with patch.object(app.tg.ptb.classes.posts, 'PostBase', autospec=True, ) as m:
        yield m

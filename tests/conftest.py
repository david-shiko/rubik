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
import datetime
from unittest.mock import create_autospec
from typing import TYPE_CHECKING, Type, Any as typing_Any
import tracemalloc
from functools import wraps
from types import GeneratorType

from psycopg2.extensions import connection as pg_ext_connection  # For spec
import pytest

import app.structures.base
import app.generation

import app.models.users
import app.models.posts
import app.models.votes
import app.models.mix
import app.forms.post
import app.forms.user

if TYPE_CHECKING:
    from unittest.mock import MagicMock

"""
# 1 https://docs.python.org/3/faq/programming.html#
    why-do-lambdas-defined-in-a-loop-with-different-values-all-return-the-same-result
"""


def get_total_memory_usage(start: tracemalloc.Snapshot, end: tracemalloc.Snapshot, ):
    top_stats = end.compare_to(start, 'lineno')
    total_memory = sum(stat.size_diff for stat in top_stats if stat.size_diff > 0) / (1024 * 1024)
    return total_memory


def trace_memory_deco(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_snapshot = tracemalloc.take_snapshot()
        result = func(*args, **kwargs)  # Execute the wrapped function
        total_memory_usage = get_total_memory_usage(start=start_snapshot, end=tracemalloc.take_snapshot(), )
        print(f"\nA Summary memory used in {func.__qualname__}:\n{total_memory_usage} MB\n")
        return result

    return wrapper

@pytest.fixture(scope='session', autouse=True, )
def tracemalloc_s():
    """For modules, clses, etc"""
    tracemalloc.start()
    yield
    tracemalloc.stop()


def trace_memory_logic(scope_name: str, ):
    start_snapshot = tracemalloc.take_snapshot()
    yield start_snapshot
    total_memory_usage = get_total_memory_usage(start=start_snapshot, end=tracemalloc.take_snapshot())
    print(f"\nTotal memory used in {scope_name}:\n{total_memory_usage} MB")


@pytest.fixture(scope='module', )
def trace_memory_module():
    yield from trace_memory_logic(scope_name="module", )


@pytest.fixture(scope='class', )
def trace_memory_class():
    yield from trace_memory_logic(scope_name="class", )


@pytest.fixture(scope='function', )
def trace_memory_func(request, ):
    yield from trace_memory_logic(scope_name=f"func {request.node.name}", )


#

@pytest.fixture(scope='session')
def frozen_datetime() -> datetime.datetime:
    result = datetime.datetime(2022, 10, 21, 14, 6, 29, 271546)
    yield result


@pytest.fixture(scope='function')
def mock_connection_f() -> MagicMock:
    yield create_autospec(spec=pg_ext_connection, spec_set=True, )


@pytest.fixture(scope='session')
def generator() -> app.generation.Generator:
    yield app.generation.generator


def get_photos() -> list[str]:
    """Real photos uploaded to telegram bot account. Values are telegram file id"""
    male = ['AgACAgIAAxkBAAKv7WFDRYye6ewbdya9j5CpdDqXa4yvAAL8sjEblVEYSlfVDEAtP5qFAQADAgADeAADIAQ',
            'AgACAgIAAxkBAAKv9GFDR08nsBeCESoCN0OqodLmjo7bAAIFszEblVEYSkxJQl29RwoKAQADAgADbQADIAQ',
            'AgACAgIAAxkBAAKv-GFDR4FCsv-qOE_LVROAN4XnC_rnAAIGszEblVEYSt8QHJ2RD1mRAQADAgADbQADIAQ',
            'AgACAgIAAxkBAAKv_GFDR7tPMCMaCSuI6X0zxdAexUNZAAIOszEblVEYSlu12UC9HH62AQADAgADeQADIAQ',
            'AgACAgIAAxkBAAKv_2FDR9rZx0COTiNyO401Jx1mfA2jAAIQszEblVEYSsTjuxcCwO30AQADAgADeAADIAQ', ]
    return male


def raise_side_effect(e: Type[Exception] | Exception, ) -> callable:
    return lambda *_, **__: app.utils.raise_(e=e, )


def get_user_config() -> app.structures.base.UserRaw:
    gender = 1
    return app.structures.base.UserRaw(
        tg_user_id=1,
        fullname='firstname1 lastname1',
        goal=1,
        gender=gender,
        age=25,
        country='country',
        city='city',
        comment='bot',
        photos=get_photos(),
    )


@pytest.fixture(scope='session')
def user_config() -> app.structures.base.UserRaw:
    yield get_user_config()


@pytest.fixture(scope='session')
def user_config_2() -> app.structures.base.UserRaw:  # TODO female photos
    yield app.structures.base.UserRaw(
        tg_user_id=2,
        fullname='firstname2 lastname2',
        goal=1,
        gender=2,
        age=25,
        country='country2',
        city='city2',
        comment='bot',
        photos=get_photos(),
    )


# # # LOGIC CLASSES # # #
@pytest.fixture(scope='session')
def public_post_form_s(user_s: app.models.users.User, ) -> app.forms.post.PublicPost:
    yield app.forms.post.PublicPost(author=user_s, message_id=1, )


@pytest.fixture(scope='function')
def mock_public_post_form(public_post_form_s: app.forms.post.PublicPost, ) -> MagicMock:
    yield create_autospec(spec=public_post_form_s, spec_set=True, )


def get_public_post(
        public_post_raw: app.structures.base.PublicPostDB,
        user: app.models.users.User,
) -> app.models.posts.PublicPost:
    public_post_raw = public_post_raw.copy()
    del public_post_raw['author']
    result = app.models.posts.PublicPost(author=user, **public_post_raw, )
    return result


@pytest.fixture(scope='session', )
def public_post_s(
        public_post_raw: app.structures.base.PublicPostDB,
        user_s: app.models.users.User,
) -> app.models.posts.PublicPost:
    result = get_public_post(public_post_raw=public_post_raw, user=user_s, )
    yield result


@pytest.fixture(scope='function', )
def mock_public_post_f(public_post_s: app.models.posts.PublicPost, ) -> MagicMock:
    mock = create_autospec(spec=public_post_s, spec_set=True, )
    mock.author.connection = public_post_s.author.connection  # Reassign mock
    yield mock


@pytest.fixture(scope='session')
def personal_post_form_s(user_s: app.models.users.User, ) -> app.forms.post.PersonalPost:
    yield app.forms.post.PersonalPost(author=user_s, message_id=1, )


@pytest.fixture(scope='function')
def personal_post_form_f(personal_post_form_s: app.forms.post.PersonalPost, ) -> app.forms.post.PersonalPost:
    yield app.forms.post.PersonalPost(author=personal_post_form_s.author, message_id=personal_post_form_s.message_id, )


@pytest.fixture(scope='function')
def mock_personal_post_form(personal_post_form_s: app.forms.post.PersonalPost, ) -> MagicMock:
    yield create_autospec(spec=personal_post_form_s, spec_set=True, )


@pytest.fixture(scope='session')
def personal_post_s(user_s, personal_post_raw: app.structures.base.PersonalPostDB, ) -> app.models.posts.PersonalPost:
    personal_post_raw = personal_post_raw.copy()
    del personal_post_raw['author']
    result = app.models.posts.PersonalPost(author=user_s, **personal_post_raw)
    yield result


@pytest.fixture(scope='function')
def mock_personal_post(personal_post_s: app.models.posts.PersonalPost, ) -> MagicMock:
    mock = create_autospec(spec=personal_post_s, spec_set=True, )
    yield mock


@pytest.fixture(scope='session')
def voted_personal_post_s(
        personal_post_s: app.models.posts.PersonalPost,
        personal_vote_s: app.models.votes.PersonalVote,
) -> app.models.posts.VotedPersonalPost:
    yield app.models.posts.VotedPersonalPost(
        post=personal_post_s,
        clicker_vote=personal_vote_s,  # The same vote is ok
        opposite_vote=personal_vote_s,  # The same vote is ok
    )


@pytest.fixture(scope='session')
def vote_s(user_s: app.models.users.User, ) -> app.models.votes.PublicVote:
    yield app.models.base.votes.VoteBase(
        user=user_s,
        post_id=1,
        message_id=1,
        value=app.models.base.votes.VoteBase.Value.POSITIVE,
    )


@pytest.fixture(scope='session')
def public_vote_db_s() -> app.structures.base.PublicVoteDB:
    vote_db = app.structures.base.PublicVoteDB(tg_user_id=1, post_id=1, message_id=1, value=None, )
    yield vote_db


@pytest.fixture(scope='session')
def public_vote_s(
        public_vote_db_s: app.structures.base.PublicVoteDB,
        user_s: app.models.users.User,
) -> app.models.votes.PublicVote:
    vote = app.models.votes.PublicVote(
        user=user_s,
        post_id=public_vote_db_s['post_id'],
        message_id=public_vote_db_s['message_id'],
        value=app.models.votes.PublicVote.Value.POSITIVE,
    )
    yield vote


@pytest.fixture(scope='function')
def mock_public_vote(public_vote_s: app.models.votes.PublicVote) -> MagicMock:
    mock = create_autospec(spec=public_vote_s, spec_set=True, )
    # mock.read_vote.return_value = mock
    yield mock


@pytest.fixture(scope='session')
def personal_vote_db_s(
        user_s: app.models.users.User,
) -> app.models.votes.PersonalVote:
    yield app.structures.base.PersonalVoteDB(
        tg_user_id=1,
        post_id=1,
        message_id=1,
        value=None,
    )


@pytest.fixture(scope='session')
def personal_vote_s(
        user_s: app.models.users.User,
        personal_vote_db_s: app.structures.base.PersonalVoteDB,
) -> app.models.votes.PersonalVote:
    vote = app.models.votes.PersonalVote(
        user=user_s,
        post_id=personal_vote_db_s['post_id'],
        message_id=personal_vote_db_s['message_id'],
        value=app.models.votes.PersonalVote.Value.POSITIVE,
    )
    yield vote


@pytest.fixture(scope='function')
def mock_personal_vote(personal_vote_s: app.models.votes.PersonalVote) -> MagicMock:
    mock = create_autospec(spec=personal_vote_s, spec_set=True, )
    yield mock


@pytest.fixture(scope='function')
def mock_public_handled_vote(public_vote_s: app.models.votes.PublicVote):
    mock_handled_vote = create_autospec(
        spec=app.models.votes.PublicVote.HandledVote(
            old_value=app.models.votes.PublicVote.Value.NEGATIVE,
            new_value=app.models.votes.PublicVote.Value.ZERO,
            incoming_value=app.models.votes.PublicVote.Value.POSITIVE,
            is_accepted=False,
        ),
        spec_set=True,
        instance=True,
    )
    yield mock_handled_vote


def get_user(user_config: app.structures.base.UserRaw, ) -> app.models.users.User:
    user_config = user_config or get_user_config()
    user = app.models.users.User(
        connection=typing_Any,
        tg_user_id=user_config['tg_user_id'],
        # tg_name='@firstname lastname',
        fullname=user_config['fullname'],
        goal=app.models.users.User.Goal(user_config['goal']),
        gender=app.models.users.User.Gender(user_config['gender']),
        age=user_config['age'],
        country=user_config['country'],
        city=user_config['city'],
        comment=user_config['comment'],
        is_registered=True,
    )
    return user


@pytest.fixture(scope='session')
def user2(user_config_2: app.structures.base.UserRaw, ) -> app.models.users.User:  # Another user
    user = app.models.users.User(
        tg_user_id=user_config_2['tg_user_id'],
        # tg_name='@firstname2 lastname2',
        fullname=user_config_2['fullname'],
        goal=app.models.users.User.Goal(user_config_2['goal']),
        gender=app.models.users.User.Gender(user_config_2['gender']),
        age=user_config_2['age'],
        country=user_config_2['country'],
        city=user_config_2['city'],
        comment=user_config_2['comment'],
    )
    yield user


@pytest.fixture(scope='function')
def target_f(user_s, user_config: app.structures.base.UserRaw, ) -> app.forms.user.Target:
    # noinspection PyTypeChecker
    yield app.forms.user.Target(
        user=user_s,
        goal=app.structures.base.Goal.BOTH,
        gender=app.forms.user.Target.Mapper.Matcher.Filters.Gender.BOTH,
        age_range=(app.structures.base.Age.MIN, app.structures.base.Age.MAX),
        country=user_config['country'],
        city=user_config['city'],
    )


@pytest.fixture(scope='session')
def target_s(user_s, ) -> app.forms.user.Target:
    yield app.forms.user.Target(
        user=user_s,
        goal=app.structures.base.Goal.BOTH,
        gender=app.forms.user.Target.Mapper.Matcher.Filters.Gender.BOTH,
        age_range=(app.structures.base.Age.MIN, app.structures.base.Age.MAX),
        country=user_s.country,
        city=user_s.city,
    )


@pytest.fixture(scope='function')
def mock_target(target_s: app.forms.user.Target, ) -> MagicMock:
    yield create_autospec(spec=target_s, spec_set=True, )


@pytest.fixture(scope='function')
def matcher(user_f: app.models.users.User, ) -> app.models.matches.Matcher:
    result = user_f.matcher
    yield result


@pytest.fixture(scope='session')
def matcher_s(user_s: app.models.users.User, ) -> app.models.matches.Matcher:
    result = user_s.matcher
    yield result


@pytest.fixture(scope='function')
def mock_matcher(matcher_s: app.models.matches.Matcher) -> MagicMock:
    result = create_autospec(spec=matcher_s, spec_set=True, )
    result.Filters.Age = app.models.matches.Matcher.Filters.Age
    result._is_unfiltered_matches_already_set = False  # Set explicitly
    yield result


@pytest.fixture(scope='session')
def match_s(user_s: app.models.users.User, user2: app.models.users.User, ) -> app.models.matches.Match:
    # TODO bind
    result = app.models.matches.Match(
        id=1,
        owner=user_s,
        user=user2,
        common_posts_count=10,
        common_posts_perc=80,
    )
    yield result


@pytest.fixture(scope='function')
def mock_match_f(match_s: app.models.matches.Match, ) -> MagicMock:
    yield create_autospec(spec=match_s, spec_set=True, )


@pytest.fixture(scope='function')
def user_f(user_config: app.structures.base.UserRaw, ) -> app.models.users.User:
    result = get_user(user_config=user_config, )
    yield result


@pytest.fixture(scope='session')
def user_s(user_config: app.structures.base.UserRaw, ) -> app.models.users.User:
    result = get_user(user_config=user_config, )
    yield result


@pytest.fixture(scope='function')
def new_user_f(user_f: app.models.users.User, ) -> app.forms.user.NewUser:
    yield app.forms.user.NewUser(
        user=user_f,
        fullname=user_f.fullname,
        goal=user_f.goal,
        gender=user_f.gender,
        age=user_f.age,
        country=user_f.country,
        city=user_f.city,
        comment=user_f.comment,
    )


@pytest.fixture(scope='function')
def match_stats(
        user_f: app.models.users.User,
        user_config_2: app.structures.base.UserRaw,
) -> app.models.mix.MatchStats:
    result = app.models.mix.MatchStats(
        user=user_f,
        with_tg_user_id=user_config_2['tg_user_id'],
        set_statistic=False,
    )
    yield result


@pytest.fixture
def unique_key_dict():
    yield app.structures.base.UniqueKeyDict()


@pytest.fixture(scope='session')
def user_s2(user_config_2: app.structures.base.UserRaw, ) -> MagicMock:
    user = get_user(user_config=user_config_2, )
    yield user


@pytest.fixture(scope='session')
def mock_user_s(
        user_s: app.models.users.User,
        collection: app.models.collections.Collection,
        collection_posts: list[app.models.posts.PersonalPost],
) -> MagicMock:
    mock_user = create_autospec(spec=user_s, spec_set=True, )
    mock_user.matcher.is_user_has_covotes = False
    yield mock_user


@pytest.fixture(scope='function')
def mock_user_f(mock_user_s: MagicMock, ) -> MagicMock:
    mock_user_s.reset_mock()
    yield mock_user_s


@pytest.fixture(scope='function')
def mock_new_user_f(new_user_f: app.forms.user.NewUser, ):
    mock = create_autospec(spec=new_user_f, spec_set=True, )
    yield mock


@pytest.fixture(scope='session')
def public_post_raw(
        user_s: app.models.users.User,
        frozen_datetime: datetime.datetime,
) -> app.structures.base.PersonalPostDB:
    yield app.structures.base.PublicPostDB(
        post_id=1,
        message_id=1,
        author=user_s.tg_user_id,
        likes_count=1,
        dislikes_count=1,
        status=app.models.posts.PublicPost.Status.PENDING.value,

    )


@pytest.fixture(scope='session')
def personal_post_raw(
        user_s: app.models.users.User,
        frozen_datetime: datetime.datetime,
) -> app.structures.base.PersonalPostDB:
    yield app.structures.base.PersonalPostDB(
        post_id=1,
        message_id=1,
        author=user_s.tg_user_id,
    )


@pytest.fixture(scope='session')
def personal_posts_raw(
        user_s: app.models.users.User,
        user_s2: app.models.users.User,
        personal_post_raw: app.structures.base.PersonalPostDB,
) -> list[app.structures.base.PersonalPostDB]:
    result = [
        personal_post_raw,
        app.structures.base.PersonalPostDB(
            post_id=2,
            message_id=1,
            author=user_s2.tg_user_id,
        ),
        app.structures.base.PersonalPostDB(
            post_id=3,
            message_id=2,
            author=user_s.tg_user_id,
        ),
        app.structures.base.PersonalPostDB(
            post_id=4,
            message_id=2,
            author=user_s2.tg_user_id,
        ),
    ]
    yield result


@pytest.fixture(scope='session')
def collection_raw(
        user_s: app.models.users.User,
        frozen_datetime: datetime.datetime,
) -> app.structures.base.CollectionDB:
    result = app.structures.base.CollectionDB(
        author=user_s.tg_user_id,
        collection_id=1,
        name='foo',

    )
    yield result


@pytest.fixture(scope='session')
def collection(
        user_s: app.models.users.User,
        collection_raw: app.structures.base.CollectionDB,
) -> app.models.collections.Collection:
    yield app.models.collections.Collection(
        author=user_s,
        collection_id=collection_raw['collection_id'],
        name=collection_raw['name'],
    )


@pytest.fixture(scope='function')
def mock_collection(collection: app.models.collections.Collection) -> MagicMock:
    yield create_autospec(spec=collection, spec_set=True, )


@pytest.fixture(scope='session')  # TODO bind with personal posts
def collection_posts(
        user_s: app.models.users.User,
        user_s2: app.models.users.User,
        personal_posts_raw: list[app.structures.base.PersonalPostDB],
) -> list[app.models.posts.PersonalPost]:
    result = []
    for post in personal_posts_raw:
        if post['author'] == user_s.tg_user_id:
            author = user_s
        else:
            author = user_s2
        post = app.models.posts.PersonalPost(author=author, post_id=post['post_id'], message_id=post['message_id'])
        result.append(post)
    yield result


@pytest.fixture
def covote() -> app.structures.base.Covote:
    # Todo bind me
    covote = app.structures.base.Covote(id=1, tg_user_id=2, count_common_interests=10, )
    yield covote


@pytest.fixture
def mock_match_stats(match_stats, ) -> MagicMock:
    mock_match_stats = create_autospec(spec=match_stats, spec_set=True, )
    yield mock_match_stats

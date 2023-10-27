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
from datetime import datetime
from dateutil.relativedelta import relativedelta

from pytest import fixture
from psycopg.rows import dict_row
from pytest_postgresql import factories

from app.db import postgres_sqls
from app.db import manager as db_manager

if TYPE_CHECKING:
    from psycopg import Connection, Cursor

postgresql_my_proc = factories.postgresql_proc()
postgresql_my = factories.postgresql(process_fixture_name='postgresql_my_proc', )  # This is fixture


@fixture(autouse=True, scope='function')
def setup(connection, ) -> None:
    db_manager.Postgres.create_app_tables(connection=connection, )


@fixture
def connection(postgresql_my) -> Connection:
    connection = postgresql_my.connection
    yield connection
    # connection.close()


@fixture
def cursor(connection) -> Cursor:
    cursor = connection.cursor(row_factory=dict_row, )
    yield cursor


@fixture
def psycopg2_connection(connection: Connection, ):
    """
    App uses psycopg2 but test framework (pytest_postgresql) uses psycopg3.
    This fixture need to manually recheck test framework results.
    """
    psycopg2_conn = db_manager.Postgres.get_connection(
        config=db_manager.Postgres.Config(
            host=connection.info.host,
            port=connection.info.port,
            user=connection.info.user,
            dbname=connection.info.dbname,
            password=connection.info.password,
        ),)
    yield psycopg2_conn


@fixture
def psycopg2_cursor(psycopg2_connection, ):
    """
    App uses psycopg2 but test framework (pytest_postgresql) uses psycopg3.
    This fixture need to manually recheck test framework results.
    """
    cursor = psycopg2_connection.cursor()
    yield cursor


def create_user(cursor: Cursor, user_id: int = 1, comment: str = 'Hello, world!', ) -> None:
    params = {  # equal to default_expected
        'tg_user_id': user_id,
        'fullname': 'Test User',
        'goal': 1,
        'gender': 1,
        'birthdate': (datetime.now() - relativedelta(years=5)).date(),
        'country': None,
        'city': None,
        'comment': comment,
    }
    cursor.execute(postgres_sqls.Users.CREATE_USER, tuple(params.values()))


def read_user(cursor, user_id: int = 1, ):
    cursor.execute(
        'SELECT tg_user_id, fullname, goal, gender, birthdate, country, city, comment FROM users WHERE id = %s',
        (user_id,)
    )
    result = cursor.fetchone()
    return result


def create_public_post(cursor: Cursor, author: int = 3, message_id: int = 2, ) -> dict:
    cursor.execute(postgres_sqls.PublicPosts.CREATE_PUBLIC_POST, (author, message_id,))
    result = cursor.fetchone()
    return result


def create_personal_post(cursor: Cursor, author: int = 3, message_id: int = 2, ) -> None:
    """No return id on create in sql"""
    params = {'author': author, 'message_id': message_id, }
    cursor.execute(postgres_sqls.PersonalPosts.CREATE_PERSONAL_POST, tuple(params.values()))


def create_public_vote(
        cursor: Cursor,
        user_id: int = 1,
        post_id: int = 1,
        message_id: int = 2,
        value: int | None = 1,
) -> None:
    # message_id=post_id - Intentionally to create different posts correspondingly for different votes
    create_public_post(cursor=cursor, author=user_id, message_id=post_id, )
    params = {'tg_user_id': user_id, 'post_id': post_id, 'message_id': message_id, 'value': value, }
    cursor.execute(postgres_sqls.PublicVotes.CREATE_PUBLIC_VOTE, tuple(params.values()))


def create_personal_vote(
        cursor: Cursor,
        user_id: int = 1,
        post_id: int = 1,
        message_id: int = 2,
        value: int = 1,
) -> None:
    # if read_user(cursor=cursor, user_id=user_id, ) is None:
    #     create_user(cursor=cursor, )
    # message_id=post_id - Intentionally to create different posts correspondingly for different votes
    create_personal_post(cursor=cursor, author=user_id, message_id=post_id, )
    params = {'tg_user_id': user_id, 'post_id': post_id, 'message_id': message_id, 'value': value, }
    cursor.execute(postgres_sqls.PersonalVotes.CREATE_PERSONAL_VOTE, tuple(params.values()))


def create_photo(cursor, user_id: int = 1, photo_file_id: str = 'foo'):
    if read_user(cursor=cursor, user_id=user_id, ) is None:
        create_user(cursor=cursor, user_id=user_id, )
    cursor.execute(postgres_sqls.Photos.CREATE_PHOTO, (user_id, photo_file_id))
    result = cursor.fetchone()
    return result


def create_shown_user(cursor, user_id: int = 1, shown_id: int = 2, ):
    """
    self.read... - to check that user not exist yet. Try/Except will break transaction, so it's not suitable.
    workflow:
    1. Check that user 1 exist, if not - create. IT's need to pass FK constraint
    2. Check that user 2 exist, if not - create. IT's need to pass FK constraint
    3. Check that user 2 exist, if not - create row itself
    """
    if read_user(cursor=cursor, user_id=user_id, ) is None:
        create_user(cursor=cursor, user_id=user_id)
    if read_user(cursor=cursor, user_id=shown_id, ) is None:
        create_user(cursor=cursor, user_id=shown_id, )
    cursor.execute(postgres_sqls.ShownUsers.CREATE_SHOWN_USER, (user_id, shown_id))


def read_shown_user(cursor, user_id: int = 1, columns: tuple = ('shown_id',), ):
    cursor.execute(f'SELECT {", ".join(columns)} FROM shown_users WHERE tg_user_id = %s', (user_id,))
    result = cursor.fetchone()
    return result

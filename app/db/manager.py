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
from types import SimpleNamespace
from dataclasses import dataclass

from psycopg2 import extras as pg_extras, ProgrammingError, errors as pg_errors, connect
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extensions import connection as pg_ext_connection, cursor as pg_ext_cursor
from psycopg2.errorcodes import READ_ONLY_SQL_TRANSACTION

from app.db.postgres_sqls import PostgresSQLS
from app.config import DB_PASSWORD
from app.db.DDL import TABLES
import app.postconfig
import app.structures.base

if TYPE_CHECKING:
    pass


class Postgres:
    """
    Create personal connection for every user
    MAKE singleton?
    What if connection are closed during an operation? Maybe check remain timeout?
    """

    sqls = PostgresSQLS
    cursor_factory = pg_extras.RealDictCursor
    tables = TABLES

    DB_MAX_CONNECTIONS = 100

    @dataclass
    class Config:
        dbname: str = 'rubik_tg_bot_db'
        user: str = 'rubik_tg_bot_user'
        password: str = DB_PASSWORD
        host: str = 'localhost'
        port: int = 5432
        connect_timeout: int = 1800

    CONFIG = Config()

    connection_pool = SimpleConnectionPool(
        minconn=1,
        maxconn=DB_MAX_CONNECTIONS,
        cursor_factory=cursor_factory,
        **vars(CONFIG),
    )
    connection: pg_ext_connection

    @classmethod
    def get_connection(cls, config: Config | None = None, ) -> pg_ext_connection:
        if config is None:
            connection = cls.connection_pool.getconn()
        else:
            connection = connect(**vars(config))
        return connection

    @classmethod
    def get_user_connection(cls, ) -> pg_ext_connection:
        """
        Proxy method to make special actions on user (not a system) connection.
        no actions currently but there usage in the code (legacy)
        """
        return cls.get_connection()

    @classmethod
    def create(cls, *args, **kwargs, ):  # pragma: no cover
        return cls.execute(*args, **kwargs)

    @classmethod
    def read(cls, *args, **kwargs, ):  # pragma: no cover
        return cls.execute(*args, **kwargs)

    @classmethod
    def update(cls, *args, **kwargs, ):  # pragma: no cover
        return cls.execute(*args, **kwargs)

    @classmethod
    def upsert(cls, *args, **kwargs, ):  # pragma: no cover
        return cls.execute(*args, **kwargs)

    @classmethod
    def delete(cls, *args, **kwargs, ):  # pragma: no cover
        return cls.execute(*args, **kwargs)

    @classmethod
    def execute(
            cls,
            statement: str,
            connection: pg_ext_connection,
            values: tuple | None = None,
            fetch: str = 'fetchone',
    ):
        with connection.cursor() as cursor:  # type: pg_ext_cursor
            try:
                result = None
                # Real execution
                cursor.execute(statement, values, )  # No keyword args cuz psycopg v2 and v3 keywords not match
                if cursor.description:  # Prevent error "no result to fetch"
                    result = getattr(cursor, fetch)()
                    result = cls.extract_result(result=result, )
                connection.commit()  # Commit even "read" ?
                return result
            except pg_errors.lookup(READ_ONLY_SQL_TRANSACTION):  # Not in use?
                connection.rollback()
                app.postconfig.logger.error('READ_ONLY_SQL_TRANSACTION')
            except (ProgrammingError, Exception) as e:
                connection.rollback()
                app.postconfig.logger.error(e)
                raise e
            finally:
                # "with" contex manager will close cursor anyway (even in case of error) but it's easiest for tests
                cursor.close()  # Do nothing

    @staticmethod
    def extract_value(item):
        """
        If the input is a dictionary with a single key-value pair or a tuple with one element,
        returns the single value. Otherwise, returns the input item unchanged.

        Args:
            item: A single item, either a dictionary, tuple or any other data type.

        Returns:
            The single value within the dictionary or tuple, if applicable, or the original item.
        """
        if isinstance(item, dict) and len(item) == 1:
            return next(iter(item.values()))
        elif isinstance(item, tuple) and len(item) == 1:
            return item[0]
        return item

    @classmethod
    def extract_result(cls, result):
        """
        Extracts values from an input that could be a single item or a list of items.
        If the input is a dictionary with a single key-value pair, a tuple with one element,
        or a list of such items, returns the single value(s).
        Otherwise, returns the input result unchanged.

        Args:
            result: The result to extract from. This could be a dictionary, tuple, list, or any other data type.

        Returns:
            The single value or list of values if the input was a single-key dictionary,
            single-element tuple or a list of such items.
            Otherwise, returns the input result (RealDictRow, not a regular dict).
        """
        if isinstance(result, (dict, tuple)):  # Fetchone
            return cls.extract_value(result)
        elif isinstance(result, list) and result:  # Fetchall
            # If it's a non-empty list and the first item is either a dict or a tuple with one item
            if isinstance(result[0], (dict, tuple)) and len(result[0]) == 1:
                return [cls.extract_value(item) for item in result]
        return result

    @classmethod
    def create_app_tables(cls, connection: pg_ext_connection | None = None):
        for table in list(cls.tables):  # table is string with sql
            cls.execute(statement=table, connection=connection or cls.connection, )


Postgres.connection = Postgres.get_connection()  # set default connection

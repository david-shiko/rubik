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

from unittest.mock import patch, ANY
from typing import TYPE_CHECKING, Any as typing_Any, Iterable

import pytest

import app.db.manager
import app.postconfig


if TYPE_CHECKING:
    from unittest.mock import MagicMock


def test_get_connection():
    with patch.object(app.db.manager.Postgres, 'connection_pool', autospec=True, ) as mock_connection_pool:
        result = app.db.manager.Postgres.get_connection()
    mock_connection_pool.getconn.assert_called_once_with()
    assert result == mock_connection_pool.getconn.return_value


def test_get_user_connection():
    with patch.object(app.db.manager.Postgres, 'get_connection', autospec=True, ) as mock_get_connection:
        result = app.db.manager.Postgres.get_user_connection()
    mock_get_connection.assert_called_once_with()
    assert result == mock_get_connection.return_value


class TestExecute:
    @staticmethod
    def test_error(mock_connection_f: MagicMock, monkeypatch, ):
        mock_cursor = mock_connection_f.cursor.return_value.__enter__.return_value
        monkeypatch.setattr(mock_cursor.fetchone, 'side_effect', ValueError)
        with patch.object(app.postconfig, 'logger', autospec=True, ) as mock_logger:
            with pytest.raises(expected_exception=ValueError):
                app.db.manager.Postgres.execute(
                    statement='foo',
                    connection=mock_connection_f,
                    values=('foo',),
                    fetch='fetchone',
                )
        mock_connection_f.rollback.assert_called_once_with()
        mock_logger.error.assert_called_once_with(ANY)  # ANY because need reproduce exception instance
        mock_cursor.close.assert_called_once_with()

    @staticmethod
    def test_success(mock_connection_f: MagicMock, ):
        mock_cursor = mock_connection_f.cursor.return_value.__enter__.return_value
        with patch.object(app.db.manager.Postgres, 'extract_result', autospec=True, ) as mock_extract_result:
            result = app.db.manager.Postgres.execute(
                statement='foo',
                connection=mock_connection_f,
                values=('foo',),
                fetch='fetchone',
            )
        mock_extract_result.assert_called_once_with(result=mock_cursor.fetchone.return_value)
        mock_cursor.execute.assert_called_once_with('foo', ('foo',), )
        assert result == mock_extract_result.return_value

    @staticmethod
    @pytest.mark.parametrize(
        argnames="item, expected",
        argvalues=[
            ({"key": "value"}, "value"),  # Testing a dictionary with a single key-value pair
            ((1,), 1),  # Testing a tuple with a single item
            ({"key1": "value1", "key2": "value2"}, {"key1": "value1", "key2": "value2"}),
            # Testing a dictionary with multiple key-value pairs
            ((1, 2), (1, 2)),  # Testing a tuple with multiple items
            (1, 1),  # Testing an integer
            ("test", "test"),  # Testing a string
        ]
    )
    def test_extract_value(item, expected):
        assert app.db.manager.Postgres.extract_value(item) == expected

    @staticmethod
    @pytest.mark.parametrize(
        argnames="result, expected",
        argvalues=[
            ({"key": "value"}, "value"),  # Testing a dictionary with a single key-value pair
            ((1,), 1),  # Testing a tuple with a single item
            ([{"key": "value"}], ["value"]),  # Testing a list with a single-key dictionary
            (["test", "test"], ["test", "test"]),  # Testing a list with multiple strings
            ([{"key1": "value1", "key2": "value2"}], [{"key1": "value1", "key2": "value2"}]),
            # Testing a list with a dictionary with multiple key-value pairs
            ([(1, 2)], [(1, 2)]),  # Testing a list with a tuple with multiple items
            ([1, 2], [1, 2]),  # Testing a list with multiple integers
            (1, 1),  # Testing an integer
            ("test", "test"),  # Testing a string
        ]
    )
    def test_extract_result(result: Iterable, expected: Iterable | int | str, ):
        assert app.db.manager.Postgres.extract_result(result) == expected


def test_create_app_tables(monkeypatch, ):
    monkeypatch.setattr(app.db.manager.Postgres, 'tables', ['foo'])
    for connection in [typing_Any, app.db.manager.Postgres.connection, ]:
        with patch.object(app.db.manager.Postgres, 'execute', autospec=True, ) as mock_execute:
            app.db.manager.Postgres.create_app_tables(connection=connection, )
        mock_execute.assert_called_once_with(statement='foo', connection=connection, )

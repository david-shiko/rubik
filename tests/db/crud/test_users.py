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
from unittest.mock import patch

import app.db.crud.users
import app.db.manager

if TYPE_CHECKING:
    pass


class TestUser:

    cls_to_test = app.db.crud.users.User

    def test_create(self, user_s: app.models.users.User, ):
        with patch.object(self.cls_to_test.db, 'create', spec_set=self.cls_to_test.db, ) as mock_create:
            self.cls_to_test.create(
                tg_user_id=user_s.tg_user_id,
                fullname=user_s.fullname,
                goal=user_s.goal,
                gender=user_s.gender,
                age=user_s.age,
                country=user_s.country,
                city=user_s.city,
                comment=user_s.comment,
                connection=user_s.connection,
            )
        mock_create.assert_called_once_with(
            connection=user_s.connection,
            statement=self.cls_to_test.db.sqls.Users.CREATE_USER,
            values=(
                user_s.tg_user_id,
                user_s.fullname,
                user_s.goal,
                user_s.gender,
                user_s.age,
                user_s.country,
                user_s.city,
                user_s.comment,
            ), )
        assert len(mock_create.mock_calls) == 1

    def test_read(self, user_s: app.models.users.User, ):
        with patch.object(self.cls_to_test.db, 'read', spec_set=self.cls_to_test.db, ) as mock_read:
            result = self.cls_to_test.read(tg_user_id=user_s.tg_user_id, connection=user_s.connection, )
        mock_read.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.Users.READ_USER,
            values=(user_s.tg_user_id,),
            connection=user_s.connection,
        )
        assert len(mock_read.mock_calls) == 1
        assert result == mock_read.return_value

    def test_upsert(self, user_s: app.models.users.User, ):
        with patch.object(self.cls_to_test.db, 'create', spec_set=self.cls_to_test.db, ) as mock_upsert:
            self.cls_to_test.upsert(
                tg_user_id=user_s.tg_user_id,
                fullname=user_s.fullname,
                goal=user_s.goal,
                gender=user_s.gender,
                age=user_s.age,
                country=user_s.country,
                city=user_s.city,
                comment=user_s.comment,
                connection=user_s.connection,
            )
        mock_upsert.assert_called_once_with(
            connection=user_s.connection,
            statement=self.cls_to_test.db.sqls.Users.UPSERT_USER,
            values=(
                user_s.tg_user_id,
                user_s.fullname,
                user_s.goal,
                user_s.gender,
                user_s.age,
                user_s.country,
                user_s.city,
                user_s.comment,
            ) * 2, )
        assert len(mock_upsert.mock_calls) == 1

    def test_delete(self, user_s: app.models.users.User, ):
        with patch.object(self.cls_to_test.db, 'delete', spec_set=self.cls_to_test.db, ) as mock_delete:
            app.db.crud.users.User.delete(tg_user_id=user_s.tg_user_id, connection=user_s.connection, )
        mock_delete.assert_called_once_with(
            statement=self.cls_to_test.db.sqls.Users.DELETE_USER,
            values=(user_s.tg_user_id,),
            connection=user_s.connection,
        )
        assert len(mock_delete.mock_calls) == 1

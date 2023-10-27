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
from typing import TYPE_CHECKING, Any as typing_Any, Type
from unittest.mock import patch, create_autospec

import pytest

from app.models.base.votes import VoteBase
from app.models.votes import PublicVote, PersonalVote
from app.tg.ptb.classes.posts import PublicPost, PersonalPost
import app.db.crud
import app.db.manager

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from app.structures.base import UserRaw, PersonalVoteDB


class TestVote:

    @staticmethod
    def test_repr(vote_s: VoteBase):
        vote_s.__repr__()

    @staticmethod
    def test_convert_vote_value():
        # "only_votable=True" on 0 value will silently set it to False cuz 0 can not be VotableValue.
        assert VoteBase.convert_vote_value(raw_value=0, only_votable=True, ) == VoteBase.Value.ZERO
        assert VoteBase.convert_vote_value(raw_value=0, only_votable=False, ) == VoteBase.Value.ZERO
        assert VoteBase.convert_vote_value(raw_value=1, only_votable=False, ) == VoteBase.Value.POSITIVE
        assert VoteBase.convert_vote_value(raw_value=4, only_votable=False, ) == VoteBase.Value.POSITIVE
        assert VoteBase.convert_vote_value(raw_value=-777, only_votable=False, ) == VoteBase.Value.NEGATIVE
        assert VoteBase.convert_vote_value(raw_value=+777, only_votable=False, ) == VoteBase.Value.POSITIVE

    @staticmethod
    def test_is_accept_vote(vote_s: VoteBase, monkeypatch, ):
        for value, expected_result in zip(sorted(vote_s.Value), (False, True, False)):
            monkeypatch.setattr(vote_s, 'value', value, )
            result = vote_s.is_accept_vote(new_vote=vote_s)
            assert result == expected_result

    class TestGetUserVote:
        @staticmethod
        def body(
                cls: Type[PublicVote | PersonalVote],
                user: app.models.users.User,
                mock_read: MagicMock,
                post: PublicPost | PersonalPost,
        ):
            result = cls.get_user_vote(user=user, post=post, )
            mock_read.assert_called_once_with(user=user, post_id=post.post_id, )
            return result

        def test_vote_found(self, mock_public_post_f: MagicMock, ):
            for cls in app.models.votes.PublicVote, app.models.votes.PersonalVote:
                with patch.object(cls, 'read', autospec=True, ) as mock_read:
                    result = self.body(cls=cls, user=typing_Any, mock_read=mock_read, post=mock_public_post_f, )
                assert result == mock_read.return_value

        def test_vote_not_found(self, public_post_s: PublicPost, monkeypatch, ):
            for cls in app.models.votes.PublicVote, app.models.votes.PersonalVote:
                with patch.object(cls, 'read', return_value=None, autospec=True, ) as mock_read:
                    result = self.body(cls=cls, user=public_post_s.author, mock_read=mock_read, post=public_post_s, )
                assert result.user == public_post_s.author
                assert result.post_id == 1
                assert result.message_id is None
                assert result.value == cls.Value.NONE


class TestPublicVote:

    @staticmethod
    @pytest.fixture(scope='function')
    def patched_crud() -> MagicMock:
        with patch.object(app.models.votes.PublicVote, 'CRUD', autospec=True, ) as mock_crud:
            yield mock_crud

    class TestReadVote:
        """read_vote"""

        @staticmethod
        def body(mock_user: MagicMock, mock_read: MagicMock, ):
            result = app.models.votes.PublicVote.read_vote(user=mock_user, post_id=1, )
            mock_read.assert_called_once_with(user=mock_user, post_id=1, )
            return result

        def test_vote_found(self, user_s: app.models.users.User, ):
            with patch.object(app.models.votes.PublicVote, 'read', autospec=True, ) as mock_read:
                result = self.body(mock_read=mock_read, mock_user=create_autospec(spec=user_s, spec_set=True, ), )
            assert result == mock_read.return_value

        def test_vote_not_found(self, mock_user_s: MagicMock, ):
            with patch.object(app.models.votes.PublicVote, 'read', autospec=True, return_value=None, ) as mock_read:
                result = self.body(mock_read=mock_read, mock_user=mock_user_s, )
            mock_read.assert_called_once_with(user=mock_user_s, post_id=1, )
            assert result.user == mock_user_s
            assert result.post_id == 1
            assert result.message_id is None
            assert result.value == app.models.votes.PublicVote.Value.ZERO

    @staticmethod
    def test_read(
            public_vote_s: app.models.votes.PublicVote,
            patched_crud: MagicMock,
            public_vote_db_s: app.structures.base.PublicVoteDB,
    ):
        patched_crud.read.return_value = public_vote_db_s
        with patch.object(app.models.votes.PublicVote, 'Value', autospec=True, ) as mock_Value:
            result = app.models.votes.PublicVote.read(post_id=1, user=public_vote_s.user, )
        mock_Value.assert_called_once_with(public_vote_db_s['value'])
        patched_crud.read.assert_called_once_with(
            post_id=1,
            tg_user_id=public_vote_s.user.tg_user_id,
            connection=public_vote_s.user.connection,
        )
        assert len(mock_Value.mock_calls) == len(patched_crud.mock_calls) == 1
        assert result.user == public_vote_s.user
        assert result.post_id == 1
        assert result.message_id == public_vote_db_s['message_id']
        assert result.value == mock_Value.return_value

    @staticmethod
    def test_update(mock_public_vote: MagicMock, ):
        app.models.votes.PublicVote.update(self=mock_public_vote, )
        mock_public_vote.CRUD.update.assert_called_once_with(
            tg_user_id=mock_public_vote.user.tg_user_id,
            connection=mock_public_vote.user.connection,
            post_id=mock_public_vote.post_id,
            value=mock_public_vote.value.value,
        )

    @staticmethod
    def test_get_user_votes(
            mock_user_s: MagicMock, public_vote_db_s: app.structures.base.PublicVoteDB,
            patched_crud: MagicMock, ):
        patched_crud.reset_mock()
        patched_crud.read_user_votes.return_value = [public_vote_db_s]
        # EXECUTION
        with patch.object(app.models.votes.PublicVote, 'Value', autospec=True, ) as mock_Value:
            result = app.models.votes.PublicVote.get_user_votes(user=mock_user_s, )
        # CHECKS
        patched_crud.read_user_votes.assert_called_once_with(
            tg_user_id=mock_user_s.tg_user_id,
            connection=mock_user_s.connection,
        )
        mock_Value.assert_called_once_with(public_vote_db_s['value'])
        assert result[0].user == mock_user_s
        assert result[0].post_id == 1
        assert result[0].message_id == public_vote_db_s['message_id']
        assert result[0].value == mock_Value.return_value
        assert len(mock_Value.mock_calls) == len(patched_crud.mock_calls) == 1
        assert len(result) == 1

    @staticmethod
    def test_handle(mock_public_vote: MagicMock, ):
        mock_self = mock_public_vote
        mock_self.read_vote.return_value.is_accept_vote.return_value = True
        # EXECUTION
        result = app.models.votes.PublicVote.handle(self=mock_self, )
        # CHECKS
        mock_self.read_vote.assert_called_once_with(user=mock_self.user, post_id=mock_self.post_id, )
        mock_self.read_vote.return_value.is_accept_vote.assert_called_once_with(new_vote=mock_self, )
        mock_self.upsert_value.assert_called_once_with()
        assert result == mock_self.HandledVote.return_value

    @staticmethod
    def test_upsert_value(mock_public_vote: MagicMock, ):
        app.models.votes.PublicVote.upsert_value(self=mock_public_vote, )
        mock_public_vote.CRUD.upsert_value.assert_called_once_with(
            tg_user_id=mock_public_vote.user.tg_user_id,
            post_id=mock_public_vote.post_id,
            message_id=mock_public_vote.message_id,
            value=mock_public_vote.value.value,
            connection=mock_public_vote.user.connection,
        )

    @staticmethod
    def test_read_user_votes_count(user_s: app.models.users.User, patched_crud: MagicMock, ):
        result = app.models.votes.PublicVote.read_user_votes_count(user=user_s, )
        patched_crud.read_user_votes_count.assert_called_once_with(
            tg_user_id=user_s.tg_user_id,
            connection=user_s.connection,
        )
        assert result == patched_crud.read_user_votes_count.return_value


class TestPersonalVote:
    class TestRead:
        @staticmethod
        def test_not_found(personal_vote_s: PersonalVote, personal_vote_db_s: PersonalVoteDB, ):
            with patch.object(app.models.votes.PersonalVote.CRUD, 'read', return_value=None, ) as mock_read:
                result = app.models.votes.PersonalVote.read(
                    user=personal_vote_s.user,
                    post_id=personal_vote_s.post_id,
                )
            # Checks
            mock_read.assert_called_once_with(
                tg_user_id=personal_vote_s.user.tg_user_id,
                post_id=personal_vote_s.post_id,
                connection=personal_vote_s.user.connection,
            )
            assert result is None

        @staticmethod
        def test_success(personal_vote_s: PersonalVote, personal_vote_db_s: PersonalVoteDB, ):
            personal_vote_db_s = personal_vote_db_s.copy()  # Del inside target func
            personal_vote_db_s['value'] = 0
            with patch.object(
                    app.models.votes.PersonalVote.CRUD, 'read',
                    return_value=personal_vote_db_s, ) as mock_read:
                result = app.models.votes.PersonalVote.read(
                    user=personal_vote_s.user,
                    post_id=personal_vote_s.post_id,
                )
            # Checks
            mock_read.assert_called_once_with(
                tg_user_id=personal_vote_s.user.tg_user_id,
                post_id=personal_vote_s.post_id,
                connection=personal_vote_s.user.connection,
            )
            assert result.value == app.models.votes.PersonalVote.Value.ZERO
            assert isinstance(result, app.models.votes.PersonalVote, )
            assert isinstance(result.value, app.models.votes.PersonalVote.Value, )

    class TestReadVote:

        @staticmethod
        def body(mock_user: MagicMock, mock_read: MagicMock, post_id: int, ):
            result = app.models.votes.PersonalVote.read_vote(user=mock_user, post_id=post_id, )
            mock_read.assert_called_once_with(user=mock_user, post_id=post_id, )
            return result

        def test_vote_found(self, mock_user_s: MagicMock):
            with patch.object(app.models.votes.PersonalVote, 'read', autospec=True) as mock_read:
                result = self.body(mock_user=mock_user_s, mock_read=mock_read, post_id=1, )
            assert result == mock_read.return_value

        def test_vote_not_found(
                self,
                mock_user_s: MagicMock,
                personal_vote_db_s: app.structures.base.PersonalVoteDB,
        ):
            with patch.object(app.models.votes.PersonalVote, 'read', autospec=True, return_value=None, ) as mock_read:
                result = self.body(mock_user=mock_user_s, mock_read=mock_read, post_id=1, )
            # CHECKS
            assert result.user == mock_user_s
            assert result.post_id == 1
            assert result.message_id is None
            assert result.value == app.models.votes.PersonalVote.Value.ZERO

    @staticmethod
    def test_upsert_value(mock_personal_vote: MagicMock, ):
        app.models.votes.PersonalVote.upsert(self=mock_personal_vote, message_id=mock_personal_vote.message_id, )
        mock_personal_vote.CRUD.upsert.assert_called_once_with(
            tg_user_id=mock_personal_vote.user.tg_user_id,
            post_id=mock_personal_vote.post_id,
            message_id=mock_personal_vote.message_id,
            value=mock_personal_vote.value.value,
            connection=mock_personal_vote.user.connection,
        )

    @staticmethod
    def test_get_user_votes(personal_vote_s: PersonalVote, personal_vote_db_s: PersonalVoteDB, ):
        # EXECUTION
        with patch.object(
                app.models.votes.PersonalVote.CRUD, 'read_user_votes',
                return_value=[personal_vote_db_s]
        ) as m:
            result = personal_vote_s.get_user_votes(user=personal_vote_s.user)
        # CHECKS
        m.assert_called_once_with(
            tg_user_id=personal_vote_s.user.tg_user_id,
            connection=personal_vote_s.user.connection,
        )
        assert isinstance(result[0], app.models.votes.PersonalVote, )
        assert len(result) == 1

    class TestHandle:

        @staticmethod
        def body(mock_self: MagicMock, ):
            # EXECUTION
            result = app.models.votes.PersonalVote.handle(self=mock_self, )
            # CHECKS
            mock_self.read_vote.assert_called_once_with(user=mock_self.user, post_id=mock_self.post_id, )
            mock_self.read_vote.return_value.is_accept_vote.assert_called_once_with(new_vote=mock_self, )
            mock_self.HandledVote(
                new_vote=mock_self,
                old_vote=mock_self.read_vote.return_value,
                is_accepted=mock_self.read_vote.return_value.is_accept_vote.return_value,
            )
            assert result == mock_self.HandledVote.return_value
            return result

        def test_accepted(self, mock_personal_vote: MagicMock, ):
            mock_personal_vote.read_vote.return_value.is_accept_vote.return_value = True
            result = self.body(mock_self=mock_personal_vote, )
            mock_personal_vote.upsert.assert_called_once_with(message_id=mock_personal_vote.message_id, )
            assert result == mock_personal_vote.HandledVote.return_value

        def test_declined(self, mock_personal_vote: MagicMock, ):
            mock_personal_vote.is_accept_vote.return_value = False
            result = self.body(mock_self=mock_personal_vote, )
            assert result == mock_personal_vote.HandledVote.return_value

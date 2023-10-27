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
from unittest.mock import patch, call
from typing import TYPE_CHECKING, Any as typing_Any, cast

import pytest

from app.models.posts import PersonalPost, PublicPost
from app.models.base.votes import VoteBase
from app.models.votes import PublicVote
from app.models.users import User
import app.forms

if TYPE_CHECKING:
    from unittest.mock import MagicMock


class TestPublicPostForm:
    @staticmethod
    def test_create(mock_public_post_form: MagicMock, ):
        app.forms.post.PublicPost.create(self=mock_public_post_form, )
        mock_public_post_form.Mapper.PublicPost.create.assert_called_once_with(
            author=mock_public_post_form.author,
            message_id=mock_public_post_form.message_id,
        )


class TestPersonalPostForm:
    @staticmethod
    def test_create(mock_personal_post_form: MagicMock, ):
        mock_personal_post_form.collection_names = {'foo', }
        app.forms.post.PersonalPost.create(self=mock_personal_post_form, )
        mock_personal_post_form.Mapper.PersonalPost.create.assert_called_once_with(
            author=mock_personal_post_form.author,
            message_id=mock_personal_post_form.message_id,
        )
        mock_personal_post_form.Mapper.Collection.create.assert_called_once_with(
            author=mock_personal_post_form.author,
            posts_ids=[mock_personal_post_form.Mapper.PersonalPost.create.return_value.post_id],
            name='foo',
        )


class TestPostBase:
    @staticmethod
    def test_get_post_by_vote(public_vote_s: app.models.votes.PublicVote, ):
        for cls in app.models.posts.PublicPost, app.models.posts.PersonalPost:
            with patch.object(cls, 'read', autospec=True, ) as mock_read:
                cls.get_post_by_vote(vote=public_vote_s, )
            mock_read.assert_called_once_with(post_id=public_vote_s.post_id, connection=public_vote_s.user.connection, )


class TestPublicPost:

    @staticmethod
    @pytest.fixture(scope='function')
    def patched_crud() -> MagicMock:
        with patch.object(app.models.posts.PublicPost, 'CRUD', autospec=True, ) as mock_crud:
            yield mock_crud

    @staticmethod
    @pytest.fixture
    def patched_db_to_cls() -> MagicMock:
        with patch.object(app.models.posts.PublicPost, 'db_to_cls', autospec=True, ) as mock_db_to_cls:
            yield mock_db_to_cls

    @staticmethod
    def test_repr(public_post_s: PublicPost):
        assert public_post_s.__repr__()

    @staticmethod
    def test_read(patched_db_to_cls: MagicMock, ):
        with patch.object(app.models.posts.PublicPost.CRUD, 'read', autospec=True, ) as mock_read:
            result = app.models.posts.PublicPost.read(post_id=1, connection=typing_Any, )
        mock_read.assert_called_once_with(post_id=1, connection=typing_Any, )
        patched_db_to_cls.assert_called_once_with(
            post_row=mock_read.return_value,
            connection=typing_Any,
        )
        assert result == patched_db_to_cls.return_value

    @staticmethod
    def test_create(public_post_s: PublicPost, patched_crud: MagicMock, ):
        result = app.models.posts.PublicPost.create(
            author=public_post_s.author,
            message_id=public_post_s.message_id,
        )
        patched_crud.create.assert_called_once_with(
            author=public_post_s.author.tg_user_id,
            message_id=public_post_s.message_id,
            connection=public_post_s.author.connection,
        )
        assert isinstance(result, app.models.posts.PublicPost, )
        assert result.post_id == patched_crud.create.return_value
        assert result.author == public_post_s.author
        assert result.message_id == public_post_s.message_id

    @staticmethod
    @pytest.mark.parametrize(argnames='status', argvalues=app.models.posts.PublicPost.Status, )
    def test_update_status(mock_public_post_f: MagicMock, status: app.models.posts.PublicPost.Status, ):
        app.models.posts.PublicPost.update_status(
            self=mock_public_post_f,
            status=status,
        )
        mock_public_post_f.CRUD.update_status.assert_called_once_with(
            post_id=mock_public_post_f.post_id,
            connection=mock_public_post_f.author.connection,
            status=status.value,
        )
        assert mock_public_post_f.status == status

    @staticmethod
    def test_update_votes_count(mock_public_post_f: MagicMock, ):
        app.models.posts.PublicPost.update_votes_count(self=mock_public_post_f, )
        mock_public_post_f.CRUD.update_votes_count.assert_called_once_with(
            post_id=mock_public_post_f.post_id,
            likes_count=mock_public_post_f.likes_count,
            dislikes_count=mock_public_post_f.dislikes_count,
            connection=mock_public_post_f.author.connection,
        )

    @staticmethod
    def test_read_exclusive(patched_crud: MagicMock, patched_db_to_cls: MagicMock, user_s: User, ):
        for status in sorted(app.models.posts.PublicPost.Status):
            post = app.models.posts.PublicPost.read_exclusive(user=user_s, status=status, )
            patched_crud.read_exclusive(
                tg_user_id=user_s.tg_user_id,
                status=status.value,
                connection=user_s.connection,
            )
            patched_db_to_cls.assert_called_once_with(
                post_row=patched_crud.read_exclusive.return_value,
                connection=user_s.connection,
            )
            assert post == patched_db_to_cls.return_value
            patched_db_to_cls.reset_mock()

    @staticmethod
    def test_read_mass(patched_db_to_cls: MagicMock, user_s: User, patched_crud: MagicMock, ):
        statuses = sorted(app.models.posts.PublicPost.Status)
        input_statuses = statuses + [None]
        final_statuses = statuses + [app.models.posts.PublicPost.Status.READY_TO_RELEASE]
        for input_status, final_status in zip(input_statuses, final_statuses, strict=True):
            # EXECUTION
            result = app.models.posts.PublicPost.read_mass(status=input_status, )
            # CHECKS
            patched_crud.read_mass.assert_called_once_with(
                connection=patched_crud.db.connection,
                status=final_status,
            )
            assert result == patched_db_to_cls.return_value
            patched_db_to_cls.reset_mock()
            patched_crud.read_mass.reset_mock()

    @staticmethod
    def test_accept_vote(user_f: User, public_post_s: PublicPost):
        for vote_value in sorted(VoteBase.Value):
            current_vote = PublicVote(
                user=user_f,
                post_id=public_post_s.post_id,
                message_id=public_post_s.message_id,
                value=vote_value,
            )
            for value in sorted(VoteBase.VotableValue):
                incoming_vote = PublicVote(
                    user=user_f,
                    post_id=public_post_s.post_id,
                    message_id=public_post_s.message_id,
                    value=value,
                )
                old_likes_count = public_post_s.likes_count
                old_dislikes_count = public_post_s.dislikes_count
                # Will update votes count
                is_accepted = public_post_s.accept_vote_value(
                    incoming_value=incoming_vote.value,
                    old_value=current_vote.value,
                )
                if current_vote.value == VoteBase.Value.ZERO and incoming_vote.value == VoteBase.Value.POSITIVE:
                    assert old_likes_count + VoteBase.Value.POSITIVE == public_post_s.likes_count
                    assert old_dislikes_count == public_post_s.dislikes_count
                elif current_vote.value == VoteBase.Value.ZERO and incoming_vote.value == VoteBase.Value.NEGATIVE:
                    assert old_dislikes_count + VoteBase.Value.POSITIVE == public_post_s.dislikes_count
                    assert old_likes_count == public_post_s.likes_count
                elif current_vote.value == VoteBase.Value.POSITIVE and incoming_vote.value == VoteBase.Value.NEGATIVE:
                    assert old_likes_count - VoteBase.Value.POSITIVE == public_post_s.likes_count
                    assert old_dislikes_count == public_post_s.dislikes_count
                elif current_vote.value == VoteBase.Value.NEGATIVE and incoming_vote.value == VoteBase.Value.POSITIVE:
                    assert old_dislikes_count - VoteBase.Value.POSITIVE == public_post_s.dislikes_count
                    assert old_likes_count == public_post_s.likes_count
                else:
                    assert is_accepted is False

    @staticmethod
    def test_db_to_cls(
            public_post_s: app.models.posts.PublicPost,
            public_post_raw: app.structures.base.PublicPostDB,
    ):
        result = app.models.posts.PublicPost.db_to_cls(post_row=public_post_raw, connection=typing_Any, )
        assert isinstance(result, app.models.posts.PublicPost)
        assert result.status == app.models.posts.PublicPost.Status.PENDING
        expected_dict = vars(public_post_s) | {'author': public_post_s.author.tg_user_id}  # author is differ
        actual_dict = vars(result) | {'author': result.author.tg_user_id}  # Only author is differ
        assert expected_dict == actual_dict

    @staticmethod
    def test_dbs_to_cls(
            public_post_s: app.models.posts.PublicPost,
            public_post_raw: app.structures.base.PublicPostDB,
            patched_db_to_cls: MagicMock,
    ):
        result = app.models.posts.PublicPost.dbs_to_cls(posts_rows=[public_post_raw], connection=typing_Any)
        patched_db_to_cls.assert_called_once_with(post_row=public_post_raw, connection=typing_Any, )
        assert isinstance(result, list)

    class TestHandleVote:
        """handle_vote"""

        @staticmethod
        def test_declined(mock_public_post_f: MagicMock, mock_public_handled_vote: MagicMock, ):
            """Nothing to handle for now"""
            mock_self = mock_public_post_f
            mock_self.accept_vote_value.return_value = False
            result = app.models.posts.PublicPost.handle_vote(self=mock_self, handled_vote=mock_public_handled_vote, )
            mock_self.accept_vote_value.assert_called_once_with(
                old_value=mock_public_handled_vote.old_value,
                incoming_value=mock_public_handled_vote.incoming_value
            )
            mock_self.update_votes_count.assert_not_called()
            assert result is False

        @staticmethod
        def test_accepted(mock_public_post_f: MagicMock, mock_public_handled_vote: MagicMock, ):
            """Nothing to handle for now"""
            mock_self = mock_public_post_f
            result = app.models.posts.PublicPost.handle_vote(self=mock_self, handled_vote=mock_public_handled_vote, )
            mock_self.accept_vote_value.assert_called_once_with(
                old_value=mock_public_handled_vote.old_value,
                incoming_value=mock_public_handled_vote.incoming_value
            )
            mock_self.update_votes_count.assert_called_once_with()
            assert result is True

    @staticmethod
    def test_get_voted_users(mock_public_post_f: MagicMock, ):
        mock_public_post_f.CRUD.read_voted_users_ids.return_value = [1]
        result = app.models.posts.PublicPost.get_voted_users(self=mock_public_post_f, connection=typing_Any, )
        mock_public_post_f.Mapper.User.assert_called_once_with(tg_user_id=1, connection=typing_Any, )
        assert result == [mock_public_post_f.Mapper.User.return_value]


class TestPersonalPost:

    @staticmethod
    @pytest.fixture(scope='class')
    def patched_crud() -> MagicMock:
        with patch.object(app.models.posts.PersonalPost, 'CRUD', autospec=True, ) as mock_crud:
            yield mock_crud

    @staticmethod
    @pytest.fixture
    def patched_db_to_cls() -> MagicMock:
        with patch.object(app.models.posts.PersonalPost, 'db_to_cls', autospec=True, ) as mock_db_to_cls:
            yield mock_db_to_cls

    @staticmethod
    def test_repr(personal_post_s: PersonalPost, ):
        assert repr(personal_post_s)

    @staticmethod
    def test_read(patched_db_to_cls: MagicMock, user_s: app.models.users.User, patched_crud: MagicMock, ):
        result = app.models.posts.PersonalPost.read(post_id=1, connection=typing_Any, author=typing_Any, )
        patched_crud.read.assert_called_once_with(post_id=1, connection=typing_Any, )
        patched_db_to_cls.assert_called_once_with(
            post_row=patched_crud.read.return_value,
            connection=typing_Any,
            author=typing_Any,
        )
        assert result == patched_db_to_cls.return_value

    @staticmethod
    def test_create(personal_post_s: PersonalPost, patched_crud: MagicMock, ):
        result = app.models.posts.PersonalPost.create(
            author=personal_post_s.author,
            message_id=personal_post_s.message_id,
        )
        patched_crud.create(
            author=personal_post_s.author.tg_user_id,
            message_id=personal_post_s.message_id,
            connection=personal_post_s.author.connection,
        )

        assert isinstance(result, app.models.posts.PersonalPost, )
        assert result.post_id == patched_crud.create.return_value
        assert result.author == personal_post_s.author
        assert result.message_id == personal_post_s.message_id

    @staticmethod
    def test_read_user_posts(
            personal_post_raw: app.structures.base.PersonalPostDB,
            personal_post_s: PersonalPost,
            patched_crud: MagicMock,
    ):
        patched_crud.read_user_posts.return_value = [personal_post_raw]
        result = app.models.posts.PersonalPost.read_user_posts(user=personal_post_s.author, )
        assert vars(result[0]) == vars(personal_post_s)

    @staticmethod
    def test_delete(patched_crud: MagicMock, ):
        result = app.models.posts.PersonalPost.delete(post_id=1, connection=typing_Any, )
        patched_crud.delete.assert_called_once_with(post_id=1, connection=typing_Any, )
        assert result == patched_crud.delete.return_value

    class TestDbToCls:
        @staticmethod
        def test_with_author(user_s: app.models.users.User, personal_post_raw: app.structures.base.PersonalPostDB, ):
            result = app.models.posts.PersonalPost.db_to_cls(
                post_row=personal_post_raw,
                connection=typing_Any,
                author=user_s,
            )
            assert vars(result) == personal_post_raw | {'author': user_s, }

        @staticmethod
        def test_without_author(personal_post_raw: app.structures.base.PersonalPostDB, ):
            with patch.object(app.models.posts.PersonalPost.Mapper, 'User') as mock_user_cls:
                result = app.models.posts.PersonalPost.db_to_cls(
                    post_row=personal_post_raw,
                    connection=typing_Any,
                )
            mock_user_cls.assert_called_once_with(tg_user_id=personal_post_raw['author'], connection=typing_Any, )
            assert vars(result) == personal_post_raw | {'author': mock_user_cls.return_value, }

    @staticmethod
    def test_bds_to_cls(
            patched_db_to_cls: MagicMock,
            user_s: app.models.users.User,
            personal_posts_raw: app.structures.base.PersonalPostDB,
    ):
        result = app.models.posts.PersonalPost.dbs_to_cls(
            posts_rows=[personal_posts_raw],
            connection=typing_Any,
        )
        patched_db_to_cls.assert_called_once_with(post_row=personal_posts_raw, connection=typing_Any, )
        assert result == [patched_db_to_cls.return_value]

    @staticmethod
    def test_handle_vote():
        """Nothing to handle for now"""
        assert app.models.posts.PersonalPost.handle_vote(handled_vote=typing_Any, ) is True


class TestVotedPublicPost:
    @staticmethod
    def test_convert(mock_user_f: MagicMock, public_post_s: PublicPost):
        result = app.models.posts.VotedPublicPost.convert(
            posts=[public_post_s],
            clicker=mock_user_f,
        )
        mock_user_f.get_vote.assert_called_once_with(post=public_post_s)
        assert result == [app.models.posts.VotedPublicPost(
            post=public_post_s,
            clicker_vote=mock_user_f.get_vote.return_value,
        )]


class TestVotedPersonalPost:
    @staticmethod
    def test_convert(mock_user_f: MagicMock, personal_post_s: PersonalPost, ):
        result = app.models.posts.VotedPersonalPost.convert(
            posts=[personal_post_s],
            clicker=mock_user_f,  # The same is ok
            opposite=mock_user_f,  # The same is ok
        )
        mock_user_f.get_vote.assert_has_calls([call(post=personal_post_s), call(post=personal_post_s), ])
        assert result == [app.models.posts.VotedPersonalPost(
            post=personal_post_s,
            clicker_vote=mock_user_f.get_vote.return_value,
            opposite_vote=mock_user_f.get_vote.return_value,
        )]

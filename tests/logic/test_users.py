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

from unittest.mock import patch
from typing import TYPE_CHECKING, Any as typing_Any

import pytest

from app.models.users import User

import app.forms.user

import app.exceptions
from app.models.mix import Photo

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from app.models.posts import PublicPost, PersonalPost
    from faker import Faker
    import app.tg.ptb.classes.users
    import app.generation


class TestUserProperties:

    @staticmethod
    def test_connection_setter(user_f: User):
        user_f.connection = typing_Any
        assert user_f.connection == typing_Any
        assert user_f._connection == typing_Any

    @staticmethod
    @pytest.mark.parametrize(argnames='flag', argvalues=(True, False), )
    def test_is_registered(user_f: User, monkeypatch, flag: bool, ):
        """Check setter and getter properties is correct"""
        # Firstly set is_registered to None cuz it only acts if value not set yet, i.e. is None.
        monkeypatch.setattr(user_f, '_is_registered', None, )
        with patch.object(user_f.CRUD.db, 'read', autospec=True, ) as mock_read:
            monkeypatch.setattr(user_f, 'is_registered', flag, )  # is_registered only acts if value is None.
        mock_read.assert_called_once_with(
            statement=user_f.CRUD.db.sqls.Users.IS_REGISTERED,
            values=(user_f.tg_user_id,),
            connection=user_f.connection
        )
        assert user_f.is_registered is flag

    @staticmethod
    def test_name_setter(user_f: User, monkeypatch):
        for incorrect_name in ['A' * (User.MAX_USER_NAME_LEN + 1), 'spaced text' * (User.MAX_USER_NAME_WORDS + 1)]:
            with pytest.raises(app.exceptions.IncorrectProfileValue):
                monkeypatch.setattr(user_f, 'fullname', incorrect_name)

    @staticmethod
    def test_goal_setter(user_f: User, monkeypatch, ):
        for goal in [4, 0, -2]:
            with pytest.raises(app.exceptions.IncorrectProfileValue):
                monkeypatch.setattr(user_f, 'goal', goal)

    @staticmethod
    def test_gender_setter(user_f: User, monkeypatch, ):
        for gender in 4, 0, -2, 32:
            with pytest.raises(app.exceptions.IncorrectProfileValue):
                monkeypatch.setattr(user_f, 'gender', gender)

    @staticmethod
    def test_age_setter(user_f: User, faker: Faker, monkeypatch, ):
        for age in ['4', '999', 'qwerty', faker.paragraph(), '01', '00wrqw']:
            with pytest.raises(app.exceptions.IncorrectProfileValue):
                monkeypatch.setattr(user_f, 'age', age)
            with pytest.raises(app.exceptions.IncorrectProfileValue):
                monkeypatch.setattr(user_f, 'age', age)

    @staticmethod
    def test_country_setter(user_f: User, faker: Faker, monkeypatch, ):
        with pytest.raises(app.exceptions.IncorrectProfileValue):
            monkeypatch.setattr(user_f, 'country', '_' * (User.MAX_COUNTRY_LEN + 1))
        for _ in range(5):
            monkeypatch.setattr(user_f, 'country', faker.current_country())
        for text in ['qqwe/sdf', 'qqwe/sdf, rwr^&$^SDFSGDSGD']:
            user_f.country = text

    @staticmethod
    def test_city_setter(user_f: User, faker: Faker, monkeypatch, ):
        with pytest.raises(app.exceptions.IncorrectProfileValue):
            monkeypatch.setattr(user_f, 'city', '_' * (User.MAX_CITY_LEN + 1))
        for _ in range(5):
            monkeypatch.setattr(user_f, 'city', faker.city())
        for text in ['qqwe/sdf', 'qqwe/sdf, rwr^&$^SDFSGDSGD']:
            user_f.city = text

    @staticmethod
    def test_comment_setter(user_f: User, faker: Faker, monkeypatch):
        monkeypatch.setattr(user_f, 'comment', 'A' * User.MAX_COMMENT_LEN)
        with pytest.raises(app.exceptions.IncorrectProfileValue):
            monkeypatch.setattr(user_f, 'comment', 'A' * (User.MAX_COMMENT_LEN + 1))
        for _ in range(10):
            monkeypatch.setattr(user_f, 'comment', faker.paragraph())


class TestUserActions:

    @staticmethod
    def test_get_new_public_post(user_f: User, ):
        with patch.object(app.models.posts.PublicPost, 'read_exclusive', autospec=True, ) as mock:
            user_f.get_new_public_post()
        mock.assert_called_once_with(user=user_f, )

    @staticmethod
    def test_get_personal_posts(user_f: User, ):
        with patch.object(app.models.posts.PersonalPost, 'read_user_posts', autospec=True, ) as mock:
            user_f.get_personal_posts()
        mock.assert_called_once_with(user=user_f, )

    @staticmethod
    def test_get_vote(
            user_s: User,
            public_post_s: PublicPost,
            personal_post_s: PersonalPost,
    ):
        for post, cls in (
                (public_post_s, app.models.votes.PublicVote),
                (personal_post_s, app.models.votes.PersonalVote)
        ):
            with patch.object(cls, 'get_user_vote', autospec=True, ) as mock_vote:
                user_s.get_vote(post=post, )
            mock_vote.assert_called_once_with(user=user_s, post=post, )

    class TestSetPublicVote:
        """set_public_vote"""

        @staticmethod
        def test_not_accepted(
                user_f: app.models.users.User,
                mock_public_vote: MagicMock,
        ):
            mock_public_vote.handle.return_value.is_accepted = False
            result = app.models.users.User.set_vote(self=user_f, vote=mock_public_vote, )
            # Checks
            mock_public_vote.handle.assert_called_once_with()
            mock_public_vote.Mapper.Post.get_post_by_vote.assert_not_called()
            assert result is False

        @staticmethod
        def test_public(
                user_f: app.models.users.User,
                mock_public_vote: MagicMock,
                mock_public_post_f: MagicMock,
        ):
            mock_public_vote.Mapper.Post.get_post_by_vote.return_value = mock_public_post_f
            mock_public_vote.handle.return_value.is_accepted = True
            result = app.models.users.User.set_vote(self=user_f, vote=mock_public_vote, )
            # Checks
            mock_public_vote.handle.assert_called_once_with()
            mock_public_vote.Mapper.Post.get_post_by_vote.assert_called_once_with(vote=mock_public_vote, )
            mock_public_post_f.handle_vote.assert_called_once_with(handled_vote=mock_public_vote.handle.return_value, )
            assert user_f.matcher.is_user_has_votes is True
            assert result == mock_public_post_f.handle_vote.return_value

        @staticmethod
        def test_personal(
                user_f,
                user_s: app.models.users.User,
                mock_personal_vote: MagicMock,
                monkeypatch,
        ):
            mock_post = mock_personal_vote.Mapper.Post.get_post_by_vote.return_value
            mock_personal_vote.handle.return_value.is_accepted = True
            result = app.models.users.User.set_vote(self=user_s, vote=mock_personal_vote, )
            mock_personal_vote.handle.assert_called_once_with()
            mock_personal_vote.Mapper.Post.get_post_by_vote.assert_called_once_with(vote=mock_personal_vote, )
            mock_post.handle_vote.assert_called_once_with(handled_vote=mock_personal_vote.handle.return_value, )
            assert result == mock_post.handle_vote.return_value

    @staticmethod
    def test_get_personal_votes(user_s: User):
        with patch.object(app.models.votes.PersonalVote, 'get_user_votes', autospec=True, ) as mock_get_user_votes:
            result = user_s.get_personal_votes()
        mock_get_user_votes.assert_called_once_with(user=user_s, )
        assert result == mock_get_user_votes.return_value

    @staticmethod
    def test_create_collection(
            mock_user_f: MagicMock,
            collection: app.models.collections.Collection,
    ):
        app.models.users.User.create_collection(self=mock_user_f, name=collection.name, posts=collection.posts, )
        mock_user_f.Mapper.Collection.create.assert_called_once_with(
            author=mock_user_f,
            name=collection.name,
            posts_ids=collection.posts,
        )

    class TestGetCollections:
        @staticmethod
        def test_get_ids(
                user_s: User,
                collection: app.models.collections.Collection,
        ):
            ids = [1, 2, ]
            assert user_s.collections == []
            with patch.object(
                    app.models.collections.Collection,
                    'get_by_ids',
                    autospec=True,
                    return_value=[collection],
            ) as mock_get_by_ids:
                result = user_s.get_collections(ids=ids, cache=False)
            mock_get_by_ids.assert_called_once_with(user=user_s, ids=ids)
            assert result == mock_get_by_ids.return_value == [collection]
            assert user_s.collections == []  # Still empty without cache flag

        @staticmethod
        def test_get_cache(
                user_f: User,
                collection: app.models.collections.Collection,
        ):
            assert user_f.collections == []
            with patch.object(
                    app.models.collections.Collection,
                    'get_user_collections',
                    autospec=True,
                    return_value=[collection],
            ) as mock_get_user_collections:
                result = user_f.get_collections(cache=True)
            mock_get_user_collections.assert_called_once_with(author=user_f, )
            assert result == mock_get_user_collections.return_value == [collection]
            assert set(result) <= set(user_f.collections)  # Assert cached

    @staticmethod
    def test_upsert_shown_post(mock_user_f: MagicMock, public_post_s: app.models.posts.PublicPost, ):
        app.models.users.User.upsert_shown_post(self=mock_user_f, new_message_id=1, public_post=public_post_s, )
        mock_user_f.Mapper.PublicVote.CRUD.upsert_message_id.assert_called_once_with(
            tg_user_id=mock_user_f.tg_user_id,
            post_id=public_post_s.post_id,
            new_message_id=1,
            connection=mock_user_f.connection,
        )


class TestUser:

    @staticmethod
    @pytest.fixture(scope='class')
    def patched_crud() -> MagicMock:
        with patch.object(app.models.users.User, 'CRUD', autospec=True, ) as mock_crud:
            yield mock_crud

    @staticmethod
    def test_repr(user_s: User):
        assert user_s.__repr__()

    @staticmethod
    def test_create(user_s: User, patched_crud: MagicMock, ):
        app.models.users.User.create(
            user=user_s,
            fullname=user_s.fullname,
            gender=user_s.gender,
            goal=user_s.goal,
            age=user_s.age,
            country=user_s.country,
            city=user_s.city,
            comment=user_s.comment,
        )
        patched_crud.create.assert_called_once_with(
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

    @staticmethod
    def test_read(user_s: app.models.users.User, patched_crud: MagicMock, ):
        result = app.models.users.User.read(user=user_s, )
        patched_crud.read.assert_called_once_with(tg_user_id=user_s.tg_user_id, connection=user_s.connection, )
        assert result.tg_user_id == user_s.tg_user_id

    @staticmethod
    def test_delete_photos(user_s: User):
        with patch.object(Photo, 'delete_user_photos', autospec=True, ) as m:
            user_s.delete_photos()
            m.assert_called_once_with(user=user_s)
        assert len(m.mock_calls) == 1

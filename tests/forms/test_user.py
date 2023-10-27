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

import pytest

import app.exceptions
from app.forms.user import Target, NewUser

if TYPE_CHECKING:
    from unittest.mock import MagicMock
    from faker import Faker
    import app.tg.ptb.classes.users
    import app.generation


class TestNewUser:

    @staticmethod
    def test_repr(new_user_f: NewUser):
        assert new_user_f.__repr__()

    @staticmethod
    def test_handle_name(new_user_f: app.forms.user.NewUser, faker, ) -> None:
        """No need to make call assertions on setters if actual == expected"""
        expected = faker.first_name()
        new_user_f.handle_name(text=expected)
        assert new_user_f.fullname == expected
        expected = f'{faker.first_name()} {faker.last_name()}'
        new_user_f.handle_name(text=expected)
        assert new_user_f.fullname == expected

    @staticmethod
    def test_handle_goal(new_user_f, faker: Faker, ) -> None:
        for _ in range(5):
            with pytest.raises(app.exceptions.IncorrectProfileValue):  # Try incorrect values
                expected = new_user_f.goal
                new_user_f.handle_goal(text=faker.word())
            assert new_user_f.goal == expected  # Assert that goal is not changed
        for enum_goal, text_goal in zip(new_user_f.Goal, app.constants.Reg.REG_GOALS, strict=True):
            new_user_f.handle_goal(text=text_goal.lower())
            assert new_user_f.goal == enum_goal

    @staticmethod
    def test_handle_gender(new_user_f, faker: Faker, ):
        for _ in range(5):
            with pytest.raises(app.exceptions.IncorrectProfileValue):  # Try incorrect values
                expected = new_user_f.gender
                new_user_f.handle_gender(text=faker.word())
            assert new_user_f.gender == expected  # Assert that goal is not changed

        for enum_gender, text_gender in zip(new_user_f.Gender, app.constants.Reg.REG_GENDERS, strict=True):
            new_user_f.handle_gender(text=text_gender)
            assert new_user_f.gender == enum_gender

    @staticmethod
    def test_handle_age(new_user_f: NewUser, faker: Faker, ) -> None:
        for age in ['4', '999', 'qwerty', faker.paragraph(), '01', '00wrqw', app.constants.Shared.Words.BACK, ]:
            with pytest.raises(app.exceptions.IncorrectProfileValue):
                new_user_f.handle_age(text=age)
        for expected_age, input_age in [
            (10, 'e1e0'), (42, 'sad4fs2'),
            (None, app.constants.Shared.Words.SKIP),
            (99, '99lk&^*'),
        ]:
            new_user_f.handle_age(text=input_age, )
            assert new_user_f.age == expected_age

    @staticmethod
    def test_handle_location_text(new_user_f: NewUser, monkeypatch, ):
        for expected_country, expected_city, location_text in [
            # ('France', 'Paris', 'France, Paris',),
            ('France', 'Paris', 'France, Paris',),
            ('Italy', 'Paris', 'Italy',),  # Preserved the last city
            (None, None, app.constants.Shared.Words.SKIP,),
            (app.constants.Shared.Words.BACK, None, app.constants.Shared.Words.BACK,),
        ]:
            new_user_f.handle_location_text(text=location_text)
            assert new_user_f.country == expected_country
            assert new_user_f.city == expected_city

    @staticmethod
    def test_add_photo(new_user_f: NewUser, ):
        for i in range(new_user_f.MAX_PHOTOS_COUNT):
            assert len(new_user_f.photos) == i
            assert new_user_f.add_photo(photo='foo', ) is True
        assert new_user_f.add_photo(photo='foo') is False
        assert len(new_user_f.photos) == new_user_f.MAX_PHOTOS_COUNT

    class TestRemovePhotos:
        @staticmethod
        def test_no_added_photos(mock_new_user_f: MagicMock, ):
            mock_new_user_f.photos = []
            result = app.forms.user.NewUser.remove_photos(self=mock_new_user_f, )
            assert result is False

        @staticmethod
        def test_success(mock_new_user_f: MagicMock, ):
            mock_new_user_f.photos = ['foo']
            result = app.forms.user.NewUser.remove_photos(self=mock_new_user_f, )
            assert mock_new_user_f.photos == []
            assert result is True

    @staticmethod
    def test_handle_comment(new_user_f: NewUser, faker: Faker, ) -> None:
        new_user_f.handle_comment(text=app.constants.Shared.Words.SKIP)
        assert new_user_f.comment is None
        for _ in range(5):
            correct_comment = faker.paragraph()
            new_user_f.handle_comment(text=correct_comment)
            assert new_user_f.comment == correct_comment

    @staticmethod
    def test_create_user(mock_new_user_f: MagicMock, ):
        mock_new_user_f.photos = ['foo', ]
        app.forms.user.NewUser.create(self=mock_new_user_f, )
        mock_new_user_f.user.CRUD.upsert.assert_called_once_with(
            tg_user_id=mock_new_user_f.user.tg_user_id,
            fullname=mock_new_user_f.fullname,
            goal=mock_new_user_f.goal,
            gender=mock_new_user_f.gender,
            age=mock_new_user_f.age,
            country=mock_new_user_f.country,
            city=mock_new_user_f.city,
            comment=mock_new_user_f.comment,
            connection=mock_new_user_f.user.connection,
        )
        mock_new_user_f.Mapper.Photo.create.assert_called_once_with(user=mock_new_user_f.user, photo='foo', )
        assert mock_new_user_f.user.is_registered is True


class TestTarget:

    @staticmethod
    def test_repr(target_s: Target):
        assert target_s.__repr__()

    @staticmethod
    def test_handle_start_search_no_votes(mock_target: MagicMock, faker: Faker, ):
        mock_target.user.matcher.is_user_has_votes = False
        with pytest.raises(expected_exception=app.exceptions.NoVotes):
            Target.handle_start_search(self=mock_target, text=faker.word())
        mock_target.user.matcher.create_unfiltered_matches.assert_called_once_with()

    @staticmethod
    def test_handle_start_search_no_covotes(mock_target: MagicMock, faker: Faker, ):
        mock_target.user.matcher.is_user_has_covotes = False
        with pytest.raises(expected_exception=app.exceptions.NoCovotes):
            Target.handle_start_search(self=mock_target, text=faker.word())
        mock_target.user.matcher.create_unfiltered_matches.assert_called_once_with()

    @staticmethod
    def test_handle_goal(target_s: Target, faker: Faker, ):
        """NewUser.handle_goal and TargetUser.handle_goal is identical for now, except self"""
        assert not all(target_s.handle_goal(goal.lower()) for goal in app.constants.Search.TARGET_GOALS)
        [setattr(target_s, 'goal', goal) for goal in target_s.Goal]
        for _ in range(5):  # Use variable
            if (word := faker.word()) not in app.constants.Search.TARGET_GOALS:
                with pytest.raises(app.exceptions.IncorrectProfileValue):
                    target_s.handle_goal(text=word)

    @staticmethod
    def test_handle_gender(target_s: Target, faker: Faker, ):
        """NewUser.handle_gender and TargetUser.handle_gender not identical"""
        [target_s.handle_gender(text=gender) for gender in app.constants.Search.TARGET_GENDERS]  # Will raise on error
        # Test failed success
        for _ in range(5):  # Use variable
            with pytest.raises(app.exceptions.IncorrectProfileValue):
                target_s.handle_gender(text=faker.word())

    @staticmethod
    def test_handle_age(target_s: Target, faker: Faker, generator: app.generation.Generator):
        """NewUser.handle_age and TargetUser.handle_age are not identical"""
        for age in [
            '', 'qwerty', faker.paragraph(), '01wrqw', app.constants.Shared.Words.SKIP, '4', '0', '9lk&^*',
            app.constants.Shared.Words.BACK,
        ]:
            with pytest.raises(app.exceptions.IncorrectProfileValue):
                target_s.handle_age(text=age)
        for age in ['25', '2525', '5025', '9999', 'sad4fs2', ]:  # True
            target_s.handle_age(text=age)
            target_s.handle_age(text=''.join([str(x) for x in generator.gen_age_range()]))  # Will be sorted anyway
        target_s.handle_age(text=app.constants.Search.Buttons.ANY_AGE)
        assert target_s.age_range == (target_s.Age.MIN, target_s.Age.MAX)

    @staticmethod
    def test_handle_show_option(target_s: Target, faker: Faker, ):
        target_s.handle_show_option(text=app.constants.Search.Buttons.SHOW_ALL)
        target_s.handle_show_option(text=app.constants.Search.Buttons.SHOW_NEW)
        with pytest.raises(app.exceptions.IncorrectProfileValue):
            target_s.handle_show_option(text=faker.word())

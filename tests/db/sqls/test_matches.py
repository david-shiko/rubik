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

from pytest import mark as pytest_mark, raises as pytest_raises
from psycopg.errors import UndefinedTable

from app.db import postgres_sqls
from app.models.base.matches import Matcher
from app.generation import generator

from .conftest import create_public_vote, create_personal_vote, create_user, create_photo, create_shown_user

if TYPE_CHECKING:
    pass

fixed_votes = [
    [+1, +1, +1, +1, +1, +1, +0, -1, -1, -1, -1, -1],  # 6 | 1 | 5
    [+1, -1, +1, +1, +0, +1, +0, +1, +1, +1, -1, -1],  # 7 | 2 | 3
    [+1, +0, +0, -1, -1, +1, +0, +0, -1, +0, -1, +1],  # 3 | 5 | 4
    [+1, +1, +1, +1, +1, +0, +1, +1, -1, +1, +0, +0],  # 8 | 3 | 1
    [-1, +0, -1, +0, -1, +0, +0, +1, +1, +1, +1, +0],  # 4 | 5 | 3
    [-1, +1, -1, -1, +1, +1, -1, +1, +1, -1, -1, +0],  # 5 | 1 | 6
    [+1, -1, +0, +0, -1, +0, +1, +0, +0, -1, -1, +1],  # 3 | 5 | 4
    [+0, +1, +0, +0, +0, -1, +1, +0, +1, +1, +0, +0],  # 4 | 7 | 1
    [+1, +0, +0, -1, -1, +1, +0, +1, -1, -1, +1, -1],  # 4 | 3 | 5
    [+0, +1, +0, +1, -1, +1, +0, +0, -1, -1, -1, +0],  # 3 | 5 | 4
    [-1, +0, -1, +1, -1, -1, +1, -1, +1, +1, +1, +1],  # 6 | 1 | 5
    [+0, +0, +1, -1, +1, +1, +1, -1, +0, +1, +1, +1],  # 7 | 3 | 2
    [-1, +0, +1, +0, +0, -1, -1, +0, -1, +0, +0, +0],  # 1 | 7 | 4
    [+1, -1, +0, +1, +1, +1, +1, -1, +1, +0, +1, +1],  # 8 | 2 | 2
    [+0, +1, -1, +0, -1, +1, -1, +0, -1, -1, +1, +0],  # 3 | 4 | 5
    [+0, -1, +1, -1, +1, -1, +1, +0, -1, -1, +1, +1],  # 5 | 2 | 5
    [+0, +1, +1, +1, +0, -1, +1, +0, +1, +1, -1, +1],  # 7 | 3 | 2
    [+1, +1, +0, -1, +0, -1, +0, -1, -1, +1, +0, +0],  # 3 | 5 | 4
    [-1, -1, +0, +0, +0, +0, +0, +0, -1, +1, -1, +0],  # 1 | 7 | 4
    [-1, +1, -1, -1, -1, +0, +0, +1, +0, -1, +1, -1],  # 3 | 3 | 6
    [-1, +0, -1, -1, +1, -1, +1, -1, -1, +0, -1, +1],  # 3 | 2 | 7
    [+0, +1, -1, -1, -1, -1, +1, -1, +0, -1, +0, +0],  # 2 | 4 | 6
    [+1, +0, -1, +1, +1, +0, -1, -1, +0, +1, -1, +1],  # 5 | 3 | 4
    [+1, -1, +1, -1, -1, +1, +1, +0, -1, +0, +0, -1],  # 4 | 3 | 5
    [+1, +1, +0, +1, +1, +1, -1, -1, +1, -1, +1, -1],  # 7 | 1 | 4
    [+0, -1, +1, +0, +1, -1, -1, -1, +0, +0, +1, -1],  # 3 | 4 | 5
    [-1, +1, +1, +1, +1, +0, +1, +1, +1, +1, +1, +0],  # 9 | 2 | 1
    [+0, -1, +0, +0, -1, +1, -1, +0, +1, +1, -1, -1],  # 3 | 4 | 5
    [+1, +1, +0, +0, -1, -1, +1, +1, -1, -1, +0, +0],  # 4 | 4 | 4
    [+1, +1, +1, -1, -1, -1, +1, +1, +1, -1, -1, -1],  # 6 | 0 | 6
]

l = [
    1,
    2,
    3
]

covotes = [
    [
        {'count_common_interests': 1, 'id': 28, 'tg_user_id': 8, },
        {'count_common_interests': 2, 'id': 2, 'tg_user_id': 11, },
        {'count_common_interests': 2, 'id': 17, 'tg_user_id': 13, },
        {'count_common_interests': 2, 'id': 6, 'tg_user_id': 19, },
        {'count_common_interests': 3, 'id': 20, 'tg_user_id': 7, },
        {'count_common_interests': 3, 'id': 24, 'tg_user_id': 20, },
        {'count_common_interests': 3, 'id': 1, 'tg_user_id': 22, },
        {'count_common_interests': 3, 'id': 11, 'tg_user_id': 28, },
        {'count_common_interests': 4, 'id': 9, 'tg_user_id': 3, },
        {'count_common_interests': 4, 'id': 21, 'tg_user_id': 12, },
        {'count_common_interests': 4, 'id': 4, 'tg_user_id': 15, },
        {'count_common_interests': 4, 'id': 19, 'tg_user_id': 16, },
        {'count_common_interests': 4, 'id': 10, 'tg_user_id': 17, },
        {'count_common_interests': 4, 'id': 25, 'tg_user_id': 18, },
        {'count_common_interests': 4, 'id': 8, 'tg_user_id': 21, },
        {'count_common_interests': 4, 'id': 5, 'tg_user_id': 26, },
        {'count_common_interests': 4, 'id': 26, 'tg_user_id': 27, },
        {'count_common_interests': 4, 'id': 12, 'tg_user_id': 29, },
        {'count_common_interests': 5, 'id': 15, 'tg_user_id': 6, },
        {'count_common_interests': 5, 'id': 3, 'tg_user_id': 9, },
        {'count_common_interests': 5, 'id': 16, 'tg_user_id': 14, },
        {'count_common_interests': 5, 'id': 27, 'tg_user_id': 23, },
        {'count_common_interests': 5, 'id': 22, 'tg_user_id': 24, },
        {'count_common_interests': 6, 'id': 18, 'tg_user_id': 2, },
        {'count_common_interests': 6, 'id': 13, 'tg_user_id': 4, },
        {'count_common_interests': 6, 'id': 14, 'tg_user_id': 10, },
        {'count_common_interests': 6, 'id': 7, 'tg_user_id': 30, },
        {'count_common_interests': 8, 'id': 23, 'tg_user_id': 25, },
    ],
    [  # User 2 (Just in case, need to add "id" field
        {'count_common_interests': 1, 'tg_user_id': 21, },
        {'count_common_interests': 1, 'tg_user_id': 15, },
        {'count_common_interests': 1, 'tg_user_id': 13, },
        {'count_common_interests': 2, 'tg_user_id': 29, },
        {'count_common_interests': 2, 'tg_user_id': 20, },
        {'count_common_interests': 2, 'tg_user_id': 18, },
        {'count_common_interests': 2, 'tg_user_id': 16, },
        {'count_common_interests': 2, 'tg_user_id': 8, },
        {'count_common_interests': 3, 'tg_user_id': 26, },
        {'count_common_interests': 3, 'tg_user_id': 19, },
        {'count_common_interests': 3, 'tg_user_id': 12, },
        {'count_common_interests': 3, 'tg_user_id': 11, },
        {'count_common_interests': 3, 'tg_user_id': 10, },
        {'count_common_interests': 3, 'tg_user_id': 7, },
        {'count_common_interests': 3, 'tg_user_id': 5, },
        {'count_common_interests': 3, 'tg_user_id': 3, },
        {'count_common_interests': 4, 'tg_user_id': 23, },
        {'count_common_interests': 4, 'tg_user_id': 9, },
        {'count_common_interests': 4, 'tg_user_id': 6, },
        {'count_common_interests': 5, 'tg_user_id': 27, },
        {'count_common_interests': 5, 'tg_user_id': 25, },
        {'count_common_interests': 5, 'tg_user_id': 24, },
        {'count_common_interests': 5, 'tg_user_id': 17, },
        {'count_common_interests': 5, 'tg_user_id': 14, },
        {'count_common_interests': 5, 'tg_user_id': 4, },
        {'count_common_interests': 6, 'tg_user_id': 30, },
        {'count_common_interests': 6, 'tg_user_id': 28, },
        {'count_common_interests': 6, 'tg_user_id': 1, },
    ],
]


def create_fixed_votes(cursor, func: callable, ):
    for i, votes_values in enumerate(fixed_votes):
        create_user(cursor=cursor, user_id=i + 1, )
        for post_id, value in enumerate(votes_values):
            # create_public_vote or create_personal_vote
            func(cursor=cursor, user_id=i + 1, post_id=post_id + 1, value=value, )


def sort_matches(matches: list[dict[str, int]]):
    """Sort by 2 keys if primary keys are equal; Matches should be sorted in the query"""
    return sorted(matches, key=lambda x: (x['count_common_interests'], x['tg_user_id']))


class Public:
    test_cls = postgres_sqls.Matches.Public
    fixed_votes = fixed_votes
    covotes = covotes

    count_users = len(fixed_votes)
    best_covote = covotes[0][-1]

    def create_user_votes_table(self, cursor, ):
        create_fixed_votes(cursor=cursor, func=create_public_vote, )
        cursor.execute(self.test_cls.CREATE_TEMP_TABLE_USER_VOTES, (1,))

    def create_matches_table(self, cursor, ):
        self.create_user_votes_table(cursor=cursor, )
        cursor.execute(self.test_cls.CREATE_TEMP_TABLE_USER_COVOTES, )
        cursor.execute(self.test_cls.FILL_TEMP_TABLE_USER_COVOTES, (1,))

    def read_all_matches(self, cursor, ):
        cursor.execute(self.test_cls.READ_ALL_MATCHES, )
        result = cursor.fetchall()
        return result


class TestPublic(Public, ):

    def test_create_temp_table_user_votes(self, cursor, ):
        """Result should be my votable votes."""
        expected = [  # Transformed covotes[0] without zero votes
            {'post_id': 1, 'value': 1},
            {'post_id': 2, 'value': 1},
            {'post_id': 3, 'value': 1},
            {'post_id': 4, 'value': 1},
            {'post_id': 5, 'value': 1},
            {'post_id': 6, 'value': 1},
            {'post_id': 8, 'value': -1},
            {'post_id': 9, 'value': -1},
            {'post_id': 10, 'value': -1},
            {'post_id': 11, 'value': -1},
            {'post_id': 12, 'value': -1},
        ]
        self.create_user_votes_table(cursor=cursor, )
        cursor.execute(self.test_cls.READ_USER_VOTES, )
        result = cursor.fetchall()
        assert result == expected

    def test_create_temp_table_user_covotes(self, cursor, psycopg2_cursor):
        """
        Test tmp table with my covotes only
        Requirements:
        1. No user_id itself, only covotes.
        2. No None votes.

        Almost the same test with test_create_temp_table_user_covotes cuz most of the actions the same:
        1. create fixed public votes.
        2. create temp table user votes.
        3. create temp table user covotes.
        4. read result.
        5. Compare result.
        """
        cursor.execute(query=f'DROP TABLE IF EXISTS {self.test_cls.TMP_COVOTES_TABLE_NAME}')
        self.create_matches_table(cursor=cursor, )
        result = self.read_all_matches(cursor=cursor, )
        assert sort_matches(matches=result, ) == sort_matches(matches=self.covotes[0], )

    def test_read_all_matches(self, cursor, ):
        """
        Almost the same test with test_create_temp_table_user_covotes cuz most of the actions the same:
        1. create fixed public votes.
        2. create temp table user votes.
        3. create temp table user covotes.
        4. read result.
        5. Compare result.
        """
        self.create_matches_table(cursor=cursor, )
        result = self.read_all_matches(cursor=cursor, )
        assert sort_matches(matches=result, ) == sort_matches(matches=self.covotes[0], )

    def test_read_new_matches(self, cursor, ):
        """
        Almost the same test with test_create_temp_table_user_covotes,
        but now it also checks for excluding already shown users.
        """
        self.create_matches_table(cursor=cursor, )
        all_matches = self.read_all_matches(cursor=cursor, )
        assert self.best_covote in all_matches
        create_shown_user(cursor=cursor, shown_id=self.best_covote['tg_user_id'], )
        cursor.execute(self.test_cls.READ_NEW_MATCHES, (1,))
        result = cursor.fetchall()
        # [:-1]  Exclude shown users (they are intentionally at the end of covotes
        expected = sort_matches(matches=self.covotes[0][:-1], )
        assert sort_matches(matches=result, ) == expected

    def test_drop_temp_table_user_votes(self, cursor):
        self.create_user_votes_table(cursor=cursor, )  # Ensure the table exists
        cursor.execute(self.test_cls.DROP_TEMP_TABLE_USER_VOTES, )
        with pytest_raises(expected_exception=UndefinedTable, ):
            cursor.execute(self.test_cls.READ_USER_VOTES, )

    def test_drop_temp_table_user_covotes(self, cursor):
        self.create_matches_table(cursor=cursor, )  # Ensure the table exists
        # Drop the table
        cursor.execute(self.test_cls.DROP_TEMP_TABLE_USER_COVOTES)
        with pytest_raises(expected_exception=UndefinedTable, ):
            cursor.execute(self.test_cls.READ_ALL_MATCHES, )

    class TestFilters(Public, ):

        @pytest_mark.parametrize(
            argnames='goal',
            argvalues=(Matcher.Filters.Goal.CHAT.value, Matcher.Filters.Goal.DATE.value,),
        )
        def test_use_goal_filter(self, cursor, goal: int, ):
            self.create_matches_table(cursor, )
            goals = list(Matcher.Filters.Goal)
            for i in range(self.count_users, ):
                goal = goals[i % len(goals)]  # Infinite looping over lst
                cursor.execute(
                    'UPDATE users SET goal = %s WHERE id = %s',
                    (goal, i + 1,),  # +1 - id starts from 1, not 0
                )
            expected_goals = (goal, Matcher.Filters.Goal.BOTH.value,)
            # Before
            cursor.execute(
                'SELECT DISTINCT goal FROM users WHERE tg_user_id IN '
                f'(SELECT tg_user_id FROM {self.test_cls.TMP_COVOTES_TABLE_NAME})'
            )
            initial_results = cursor.fetchall()
            assert any(initial_result['goal'] not in expected_goals for initial_result in initial_results)
            # Execution
            cursor.execute(self.test_cls.USE_GOAL_FILTER, (goal,))
            # Checks
            cursor.execute(
                'SELECT DISTINCT goal FROM users WHERE tg_user_id IN '
                f'(SELECT tg_user_id FROM {self.test_cls.TMP_COVOTES_TABLE_NAME})'
            )
            results = cursor.fetchall()
            assert all(result['goal'] in expected_goals for result in results)

        @pytest_mark.parametrize(
            argnames='gender',
            argvalues=(Matcher.Filters.Gender.MALE.value, Matcher.Filters.Gender.FEMALE.value,),
        )
        def test_use_gender_filter(self, cursor, gender: int, ):
            expected_genders = (gender, Matcher.Filters.Gender.BOTH.value,)
            self.create_matches_table(cursor, )
            # Before
            genders = list(Matcher.Filters.Gender)
            for i in range(self.count_users, ):
                gender = genders[i % len(genders)]  # Infinite looping over lst
                cursor.execute(
                    'UPDATE users SET gender = %s WHERE id = %s',
                    (gender, i + 1,),  # i + 1 - id starts from 1, not 0
                )
            cursor.execute(
                'SELECT DISTINCT gender FROM users WHERE tg_user_id IN '
                f'(SELECT tg_user_id FROM {self.test_cls.TMP_COVOTES_TABLE_NAME})'
            )
            initial_results = cursor.fetchall()
            assert any(initial_result['gender'] not in expected_genders for initial_result in initial_results)
            # Execution
            cursor.execute(self.test_cls.USE_GENDER_FILTER, (gender,))
            cursor.execute(
                'SELECT DISTINCT gender FROM users WHERE tg_user_id IN '
                f'(SELECT tg_user_id FROM {self.test_cls.TMP_COVOTES_TABLE_NAME})'
            )
            results = cursor.fetchall()
            assert all(result['gender'] in expected_genders for result in results)

        @pytest_mark.parametrize(
            argnames='min_age, max_age',
            argvalues=[(18, 25), (26, 35), (36, 45)],
        )
        def test_use_age_filter(self, cursor, min_age: int, max_age: int, ):
            self.create_matches_table(cursor, )
            # Before
            for i in range(self.count_users, ):
                cursor.execute(
                    "UPDATE users SET birthdate = CURRENT_DATE - INTERVAL '%s YEAR' WHERE id = %s",
                    (generator.gen_age(), i + 1,),  # i + 1 - id starts from 1, not 0
                )
            cursor.execute(
                "SELECT DISTINCT date_part('year', age(birthdate)) as age FROM users WHERE tg_user_id IN "
                f"(SELECT tg_user_id FROM {self.test_cls.TMP_COVOTES_TABLE_NAME})"
            )
            initial_results = cursor.fetchall()
            assert any(not (min_age <= initial_result['age'] <= max_age) for initial_result in initial_results)
            cursor.execute(self.test_cls.USE_AGE_FILTER, (min_age, max_age,))
            cursor.execute(
                "SELECT date_part('year', age(birthdate)) as age FROM users WHERE tg_user_id IN "
                f"(SELECT tg_user_id FROM {self.test_cls.TMP_COVOTES_TABLE_NAME})"
            )
            results = cursor.fetchall()
            assert all(min_age <= result['age'] <= max_age for result in results)

        def test_use_photo_filter(self, cursor):
            self.create_matches_table(cursor, )
            # Before
            cursor.execute(f'SELECT * from PHOTOS', )
            assert cursor.fetchall() == []  # No users with photos (at all and matches correspondingly)
            create_photo(cursor=cursor, user_id=self.best_covote['tg_user_id'], )
            # Execution
            cursor.execute(self.test_cls.USE_CHECKBOX_PHOTO_FILTER)
            result = self.read_all_matches(cursor=cursor, )
            assert result == [self.best_covote, ]  # Only users with photos are left

        def test_use_country_filter(self, cursor):
            self.create_matches_table(cursor, )
            # Before
            cursor.execute(f'SELECT * from USERS WHERE COUNTRY IS NOT NULL', )
            assert cursor.fetchall() == []  # No users with countries (at all and matches correspondingly)
            cursor.execute("UPDATE users SET country = 'Foo' WHERE id = %s", (self.best_covote['tg_user_id'],), )
            # Execution
            cursor.execute(self.test_cls.USE_CHECKBOX_COUNTRY_FILTER)
            result = self.read_all_matches(cursor=cursor, )
            assert result == [self.best_covote, ]  # Only users with photos are left

        def test_use_city_filter(self, cursor):
            self.create_matches_table(cursor, )
            # Before
            cursor.execute(f'SELECT * from USERS WHERE CITY IS NOT NULL', )
            assert cursor.fetchall() == []  # No users with cities (at all and matches correspondingly)
            cursor.execute("UPDATE users SET city = 'Foo' WHERE id = %s", (self.best_covote['tg_user_id'],), )
            # Execution
            cursor.execute(self.test_cls.USE_CHECKBOX_CITY_FILTER, )
            result = self.read_all_matches(cursor=cursor, )
            assert result == [self.best_covote, ]  # Only users with photos are left

    def test_is_user_has_covotes(self, cursor):
        self.create_matches_table(cursor, )
        cursor.execute(self.test_cls.IS_USER_HAS_COVOTES)
        results = cursor.fetchone()
        assert results is not None  # Covotes are present
        # Clean the covotes table
        cursor.execute(f'DELETE FROM {self.test_cls.TMP_COVOTES_TABLE_NAME}')
        cursor.execute(self.test_cls.IS_USER_HAS_COVOTES)
        results = cursor.fetchone()
        assert results is None  # Covotes are not present


class TestPersonal:
    test_cls = postgres_sqls.Matches.Personal

    def create_user_votes_table(self, cursor, ):
        create_fixed_votes(cursor=cursor, func=create_personal_vote, )
        cursor.execute(self.test_cls.CREATE_TEMP_TABLE_PERSONAL_VOTES, (1,))

    def create_user_covotes_table(self, cursor, ):
        """Covotes for personal votes is table with my and some other user"""
        self.create_user_votes_table(cursor=cursor, )
        cursor.execute(self.test_cls.CREATE_TEMP_TABLE_MY_AND_COVOTE_PERSONAL_VOTES, (1, 2, 1), )  # my id, opposite, my

    def test_create_temp_table_personal_votes(self, cursor):
        expected = [  # Transformed covotes[0]
            {'post_id': 1, 'value': 1},
            {'post_id': 2, 'value': 1},
            {'post_id': 3, 'value': 1},
            {'post_id': 4, 'value': 1},
            {'post_id': 5, 'value': 1},
            {'post_id': 6, 'value': 1},
            {'post_id': 7, 'value': 0},
            {'post_id': 8, 'value': -1},
            {'post_id': 9, 'value': -1},
            {'post_id': 10, 'value': -1},
            {'post_id': 11, 'value': -1},
            {'post_id': 12, 'value': -1},
        ]
        self.create_user_votes_table(cursor=cursor, )
        cursor.execute(f"SELECT * FROM {self.test_cls.TMP_PERSONAL_VOTES_TABLE_NAME}")
        result = cursor.fetchall()
        assert result == expected

    def test_create_temp_table_my_and_covote_personal_votes(self, cursor):
        expected = [  # Covotes of me and user with id 2 (covotes[1]
            {'post_id': 1, 'tg_user_id': 1, 'value': 1},
            {'post_id': 2, 'tg_user_id': 1, 'value': 1},
            {'post_id': 3, 'tg_user_id': 1, 'value': 1},
            {'post_id': 4, 'tg_user_id': 1, 'value': 1},
            {'post_id': 5, 'tg_user_id': 1, 'value': 1},
            {'post_id': 6, 'tg_user_id': 1, 'value': 1},
            {'post_id': 7, 'tg_user_id': 1, 'value': 0},
            {'post_id': 8, 'tg_user_id': 1, 'value': -1},
            {'post_id': 9, 'tg_user_id': 1, 'value': -1},
            {'post_id': 10, 'tg_user_id': 1, 'value': -1},
            {'post_id': 11, 'tg_user_id': 1, 'value': -1},
            {'post_id': 12, 'tg_user_id': 1, 'value': -1},
            {'post_id': 1, 'tg_user_id': 2, 'value': 1},
            {'post_id': 3, 'tg_user_id': 2, 'value': 1},
            {'post_id': 4, 'tg_user_id': 2, 'value': 1},
            {'post_id': 6, 'tg_user_id': 2, 'value': 1},
            {'post_id': 7, 'tg_user_id': 2, 'value': 0},
            {'post_id': 11, 'tg_user_id': 2, 'value': -1},
            {'post_id': 12, 'tg_user_id': 2, 'value': -1},
        ]
        self.create_user_votes_table(cursor=cursor, )
        cursor.execute(self.test_cls.CREATE_TEMP_TABLE_MY_AND_COVOTE_PERSONAL_VOTES, (1, 2, 1), )  # my id, opposite, my
        cursor.execute(f"SELECT * FROM {self.test_cls.TMP_PERSONAL_COVOTES_TABLE_NAME}")
        result = cursor.fetchall()
        assert result == expected

    def test_read_user_personal_votes_statistic(self, cursor):
        """Test my votes/stats"""
        expected = {
            'num_pos_votes': fixed_votes[0].count(1),
            'num_neg_votes': fixed_votes[0].count(-1),
            'num_zero_votes': fixed_votes[0].count(0),
        }
        self.create_user_covotes_table(cursor, )
        cursor.execute(self.test_cls.READ_USER_PERSONAL_VOTES_STATISTIC, (1,))  # Assuming 1 is the user id
        result = cursor.fetchone()
        assert result == expected

    def test_read_personal_covotes_count(self, cursor):
        """Test other user (passing my id for simplicity"""
        expected = {
            'num_pos_votes': fixed_votes[0].count(1),
            'num_neg_votes': fixed_votes[0].count(-1),
            'num_zero_votes': fixed_votes[0].count(0),
        }
        self.create_user_covotes_table(cursor, )
        cursor.execute(self.test_cls.READ_PERSONAL_COVOTES_COUNT, (1,))  # Assuming 1 is the user id
        result = cursor.fetchone()
        assert result == expected

    def test_drop_temp_table_personal_votes(self, cursor):
        cursor.execute(self.test_cls.CREATE_TEMP_TABLE_PERSONAL_VOTES, (1,))
        cursor.execute(f"DROP TABLE IF EXISTS {self.test_cls.TMP_PERSONAL_VOTES_TABLE_NAME}")
        with pytest_raises(UndefinedTable):
            cursor.execute(f"SELECT * FROM {self.test_cls.TMP_PERSONAL_VOTES_TABLE_NAME}")

    def test_drop_temp_table_my_and_covote_personal_votes(self, cursor):
        cursor.execute(self.test_cls.CREATE_TEMP_TABLE_MY_AND_COVOTE_PERSONAL_VOTES, (1, 2, 1))
        cursor.execute(f"DROP TABLE IF EXISTS {self.test_cls.TMP_PERSONAL_COVOTES_TABLE_NAME}")
        with pytest_raises(UndefinedTable):
            cursor.execute(f"SELECT * FROM {self.test_cls.TMP_PERSONAL_COVOTES_TABLE_NAME}")

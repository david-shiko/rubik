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
from random import Random
from typing import TYPE_CHECKING

# noinspection PyPackageRequirements
from telegram.error import BadRequest
from faker import Faker

from app.constants import I_AM_BOT
from app.structures.base import UserDB
import app.models.users
import app.models.posts
import app.models.votes
import app.forms.user

if TYPE_CHECKING:
    pass
    # from app.models.votes import PublicVote, PersonalVote
    # from app.models.posts import PublicPost, PersonalPost


class Generator:
    REAL_USERS_IDS = [177381168, 5064404775, 1262442213]
    DEFAULT_POSTS_TO_GEN = 10
    DEFAULT_COUNTRY_CHANCE = CITY_CHANCE = 75
    DEFAULT_POST_MESSAGE_ID = 71391

    MALE_PHOTOS = (
        'AgACAgIAAxkDAAISaGRt0irPsFkbxqin2hjFdnWzEWzOAAKTyDEb4dpwS2vqOBmLJYTyAQADAgADeAADLwQ',
        'AgACAgIAAxkDAAISaWRt0ivVTL8lPr8y7J3hnB8DymXsAAKUyDEb4dpwS1mRtB9Ep6doAQADAgADbQADLwQ',
        'AgACAgIAAxkDAAISamRt0isPQEGlu63BVFOStVWbNduqAAKVyDEb4dpwS0Ehf14zKmAjAQADAgADeAADLwQ',
        'AgACAgIAAxkDAAISa2Rt0iveM6nZMkxi5v-_5OskK5cgAAKWyDEb4dpwS-4FvHzX1VScAQADAgADbQADLwQ',
        'AgACAgIAAxkDAAISbGRt0iziiNmtw0bGqDJlBW82cZDAAAKXyDEb4dpwSy3Pa9RwiIB5AQADAgADeQADLwQ',
    )
    FEMALE_PHOTOS = (
        'AgACAgIAAxkDAAISbWRt0izc2-apOSopRlKr1oHOqTXHAAKcyDEb4dpwS7ijBri3XRheAQADAgADeAADLwQ',
        'AgACAgIAAxkDAAISbmRt0izZNk52Nj6mbG5x10SpwpDeAAKdyDEb4dpwS8RhgzUXKAgRAQADAgADeAADLwQ',
        'AgACAgIAAxkDAAISb2Rt0ixYhCfMaQIn348_k2yt8Wa0AAKeyDEb4dpwS6zocmZZ7-qbAQADAgADeAADLwQ',
        'AgACAgIAAxkDAAIScGRt0i1srx3ZC2RJ2KlHHMgK1u_xAAKfyDEb4dpwS1Z1cioexv65AQADAgADeAADLwQ',
        'AgACAgIAAxkDAAIScWRt0i2Gek9jn0pS2TNi7UJuaV4pAAKgyDEb4dpwSw-QXlke8MjFAQADAgADbQADLwQ',
    )

    def validate_photos(self, bot):
        for i, photo in enumerate(self.MALE_PHOTOS + self.FEMALE_PHOTOS):
            try:
                bot.get_file(photo)
            except BadRequest as e:  # Invalid file_id
                raise Exception(
                    f'file id of photo with index {i} was obsolete and need to be replaced\n'
                    f'Try to use _set_cls_photos cls method to access new file ids\n'
                    f'Original error: {e}'
                    )

    def __init__(
            self,
            faker: Faker | None = None,
            random_inst: Random | None = None,
    ):
        self.seed_num = 0
        self.faker = faker or Faker('ru_RU')
        self.random = random_inst or Random(self.seed_num)  # Use seed instead of "Random" cls ?
        self.faker.seed_instance(self.seed_num)

    def chance(self, perc: int = 50) -> bool:  # Google random bit
        return True if perc > self.random.randint(0, 100) else False

    def gen_fullname(self, gender: app.models.users.User.Gender = None) -> str:
        if gender == app.models.users.User.Gender.MALE:
            name = self.faker.unique.name_male()
        else:
            name = self.faker.unique.name_female()
        if len(name.split(' ')) > app.models.users.User.MAX_USER_NAME_WORDS:
            # First word may be "mr" or "doctor"
            name = ' '.join(name.split(' ')[-app.models.users.User.MAX_USER_NAME_WORDS:])
        return name

    def gen_goal(self) -> app.models.users.User.Goal:
        return self.random.choice(list(app.models.users.User.Goal))  # List is required

    def gen_gender(self) -> app.models.users.User.Gender:
        return self.random.choice(list(app.models.users.User.Gender))  # List is required

    def gen_age(
            self,
            min_age: int = app.models.users.User.Age.MIN,
            max_age: int = app.models.users.User.Age.MAX,
    ) -> int:
        return self.random.randint(min_age, max_age)

    def gen_age_range(
            self,
            min_age: int = app.models.users.User.Age.MIN,
            max_age: int = app.models.users.User.Age.MAX,
    ) -> tuple[int, int]:
        max_lowest_age = self.random.randint(min_age, max_age)
        return (
            self.random.randint(min_age, max_lowest_age),
            self.random.randint(max_lowest_age, app.models.users.User.Age.MAX),
        )

    def gen_country(self, chance: int = None) -> str | None:
        if self.chance(perc=chance if chance is not None else self.DEFAULT_COUNTRY_CHANCE):
            return self.faker.current_country()  # current_country are the same for particular locales of faker instance

    def gen_city(self, chance: int = None) -> str | None:
        return self.faker.city_name() if self.chance(perc=chance if chance is not None else self.CITY_CHANCE) else None

    def gen_comment(self, comment_len: int = 20) -> str:
        return self.faker.text(max_nb_chars=comment_len)

    def gen_post_data(self) -> dict:
        return {'text': self.faker.text(), 'photo': 'foo'}

    def gen_photos(self, gender: app.models.users.User.Gender = None, count: int = None) -> list[str]:
        count = count or self.random.randint(1, len(self.MALE_PHOTOS))
        photos = self.MALE_PHOTOS if gender == app.models.users.User.Gender.MALE else self.FEMALE_PHOTOS
        return self.random.sample(photos, count)

    def gen_user_db(
            self,
            tg_user_id: int,
            fullname: str | Ellipsis = ...,
            goal: int | Ellipsis = ...,
            gender: int | Ellipsis = ...,
            age: int | Ellipsis = ...,
            country: str | Ellipsis = ...,
            city: str | Ellipsis = ...,
            comment: str | Ellipsis = ...
    ) -> UserDB:
        gender = gender if gender is not ... else self.gen_gender()
        country = country if country is not ... else self.gen_country()
        if gender == app.models.users.User.Gender.MALE:
            name = fullname if fullname is not ... else self.gen_fullname(gender=app.models.users.User.Gender.MALE)
        else:
            name = fullname if fullname is not ... else self.gen_fullname(gender=app.models.users.User.Gender.FEMALE)
        if comment is ... and tg_user_id in self.REAL_USERS_IDS:
            comment = self.gen_comment()
        elif comment is ...:
            comment = I_AM_BOT
        if country is None:
            city = None
        elif city is ...:
            city = self.gen_city()
        return UserDB(
            tg_user_id=tg_user_id,
            fullname=name,
            goal=goal if goal is not ... else self.gen_goal().value,
            gender=gender,
            age=age if age is not ... else self.gen_age(),
            country=country,
            city=city,
            comment=comment, )

    def gen_user(
            self,
            tg_user_id: int | None = None,
            user_db: UserDB | None = None,
            photos: list[str] | None = None,
    ) -> app.models.users.User:
        user_db = user_db or self.gen_user_db(tg_user_id=tg_user_id)  # Now user_db contain id 100%
        if user_db['tg_user_id'] is None:
            raise Exception('tg_user_id not provided (both "tg_user_id" and "user_db["tg_user_id"]" is None)')
        photos = photos or self.gen_photos(gender=app.models.users.User.Gender(user_db['gender']))
        return app.models.users.User(
            photos=photos,
            is_registered=False,  # False or True ?
            **self.gen_user_db(**user_db),
        )

    def gen_new_user(
            self,
            tg_user_id: int = None,
            user: app.models.users.User = None,
    ) -> app.forms.user.NewUser:
        user = user or self.gen_user(tg_user_id=tg_user_id)
        if user.tg_user_id is None:  # passed "user_db" should have "user_id", a generated one
            raise Exception('tg_user_id not provided (both "tg_user_id" and "user.tg_user_id is None)')
        return app.forms.user.NewUser(
            user=user,
            fullname=user.fullname,
            goal=user.goal,
            gender=user.gender,
            age=user.age,
            country=user.country,
            city=user.city,
            comment=user.comment,
            photos=user.photos,
        )

    def gen_vote_value(self):
        return self.random.choice(list(app.models.base.votes.VoteBase.Value))

    def gen_vote(
            self,
            user: app.models.users.User,
            post: app.models.posts.PublicPost | app.models.posts.PersonalPost,
    ) -> app.models.votes.PublicVote | app.models.votes.PersonalVote:
        return post.Mapper.Vote(
            user=user,
            post_id=post.post_id,
            message_id=post.post_id,  # Any id is ok (?)
            value=self.gen_vote_value(),
        )


# Causing import error, "no such module" if "import" and circular import if "from"
generator = Generator()  # Probably better to use the same instance over all the code

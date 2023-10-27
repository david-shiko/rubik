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

from typing import Type


class Matches:
    class Public:
        TMP_VOTES_TABLE_NAME = 'user_votes'
        TMP_COVOTES_TABLE_NAME = TMP_MATCHES_TABLE_NAME = 'user_covotes'
        READ_USER_VOTES = f'SELECT post_id, value  FROM {TMP_VOTES_TABLE_NAME}'

        READ_USER_VOTES_VALUE = f'SELECT value FROM {TMP_VOTES_TABLE_NAME}'

        READ_USER_VOTES_COUNT = f'SELECT COUNT(*) FROM {TMP_VOTES_TABLE_NAME}'

        READ_USER_COVOTES_COUNT = f'SELECT COUNT(*) FROM {TMP_COVOTES_TABLE_NAME}'

        CREATE_TEMP_TABLE_USER_VOTES = (  # Consider indexes usage for tmp table
            f'CREATE TEMPORARY TABLE IF NOT EXISTS {TMP_VOTES_TABLE_NAME} AS '
            '(SELECT post_id, value  FROM public_votes WHERE tg_user_id = %s AND value != 0)'
        )

        CREATE_TEMP_TABLE_USER_COVOTES = (
            f'CREATE TEMPORARY TABLE IF NOT EXISTS {TMP_COVOTES_TABLE_NAME} '
            f'(id SERIAL PRIMARY KEY, tg_user_id BIGINT, count_common_interests INT)'
        )

        FILL_TEMP_TABLE_USER_COVOTES = (
            f'INSERT INTO {TMP_COVOTES_TABLE_NAME} (tg_user_id, count_common_interests) '
            f'SELECT tg_user_id, COUNT(tg_user_id) FROM public_votes '
            f'WHERE (post_id, value) IN ({READ_USER_VOTES}) AND tg_user_id != %s '
            f'GROUP BY tg_user_id'
        )

        USE_GOAL_FILTER = (
            f'DELETE FROM {TMP_COVOTES_TABLE_NAME} WHERE tg_user_id NOT IN '
            '(SELECT tg_user_id FROM users WHERE goal = %s)'
        )

        USE_GENDER_FILTER = (
            f'DELETE FROM {TMP_COVOTES_TABLE_NAME} WHERE tg_user_id NOT IN '
            '(SELECT tg_user_id FROM users WHERE gender = %s)'
        )

        # First is min_age, second is max_age
        USE_AGE_FILTER = (
            f"DELETE FROM {TMP_COVOTES_TABLE_NAME} WHERE tg_user_id NOT IN "
            "(SELECT tg_user_id FROM users WHERE "
            "date_part('year', age(birthdate)) >=  %s and date_part('year', age(birthdate)) <= %s)"
        )

        USE_CHECKBOX_PHOTO_FILTER = (
            f'DELETE FROM {TMP_COVOTES_TABLE_NAME} WHERE tg_user_id NOT IN (SELECT DISTINCT tg_user_id FROM photos)'
        )

        USE_CHECKBOX_COUNTRY_FILTER = (
            f'DELETE FROM {TMP_COVOTES_TABLE_NAME} WHERE tg_user_id NOT IN '
            '(SELECT tg_user_id FROM users WHERE country IS NOT NULL)'
        )

        USE_CHECKBOX_CITY_FILTER = (
            f'DELETE FROM {TMP_COVOTES_TABLE_NAME} WHERE tg_user_id NOT IN '
            '(SELECT tg_user_id FROM users WHERE city IS NOT NULL)'
        )

        IS_USER_HAS_COVOTES = f'SELECT 1 FROM {TMP_COVOTES_TABLE_NAME} LIMIT 1'

        READ_MATCHES_PATTERN = (
            f'SELECT '
            f'{TMP_COVOTES_TABLE_NAME}.id, '
            f'{TMP_COVOTES_TABLE_NAME}.tg_user_id, '
            f'{TMP_COVOTES_TABLE_NAME}.count_common_interests FROM '
            f'{TMP_COVOTES_TABLE_NAME}'
        )

        READ_ALL_MATCHES = f'{READ_MATCHES_PATTERN} ORDER BY count_common_interests ASC'

        READ_NEW_MATCHES = (
            # Perform left join, - the standard solution to select all fields which are not in some another table.
            # Python equivalent - set(A) - set(B);
            # The same as "SELECT x FROM A WHERE id NOT IN (...)" but with better performance,
            # NOT IN (...) will be checked for every row.
            # Left join will append fields from target table to the result table.
            # Strategy:
            # 1. Read all matches.
            # 2. Detect which fields are NULL by join condition
            # 3. Remove rows with null shown_id (any field may be used indeed) from a result table.
            f'{READ_MATCHES_PATTERN} LEFT JOIN shown_users ON '
            f'{TMP_COVOTES_TABLE_NAME}.tg_user_id = shown_users.shown_id AND shown_users.tg_user_id = %s '
            f'WHERE shown_users.shown_id IS NULL '
            f'ORDER BY count_common_interests ASC'
        )

        DROP_TEMP_TABLE_USER_VOTES = f'DROP TABLE IF EXISTS {TMP_VOTES_TABLE_NAME}'

        DROP_TEMP_TABLE_USER_COVOTES = f'DROP TABLE IF EXISTS {TMP_COVOTES_TABLE_NAME}'

    class Personal:
        TMP_PERSONAL_VOTES_TABLE_NAME = 'user_personal_votes'
        TMP_PERSONAL_COVOTES_TABLE_NAME = 'my_and_covote_personal_votes'

        CREATE_TEMP_TABLE_PERSONAL_VOTES = (  # For stats reading
            f'CREATE TEMPORARY TABLE {TMP_PERSONAL_VOTES_TABLE_NAME} AS '
            '(SELECT post_id, value  FROM personal_votes WHERE tg_user_id = %s)'
        )

        CREATE_TEMP_TABLE_MY_AND_COVOTE_PERSONAL_VOTES = (
            f'CREATE TEMPORARY TABLE {TMP_PERSONAL_COVOTES_TABLE_NAME} AS '
            '(SELECT tg_user_id, post_id, value  FROM personal_votes WHERE '
            '(tg_user_id = %s OR tg_user_id = %s) AND '
            '(post_id, value) IN (SELECT  post_id, value  FROM personal_votes WHERE tg_user_id = %s))')

        # Stats/votes for other user (need verify usage)
        READ_USER_PERSONAL_VOTES_STATISTIC = (
            'SELECT '
            '    COUNT(CASE WHEN value = +1 THEN 1 END) AS num_pos_votes, '
            '    COUNT(CASE WHEN value = -1 THEN 1 END) AS num_neg_votes, '
            '    COUNT(CASE WHEN value = 0 THEN 1 END) AS num_zero_votes '
            f'FROM {TMP_PERSONAL_COVOTES_TABLE_NAME} WHERE tg_user_id = %s'
        )

        # Stats/votes for me (need verify usage)
        READ_PERSONAL_COVOTES_COUNT = (
            f'SELECT '
            f'COUNT(CASE WHEN value = 1 THEN 1 END) AS num_pos_votes, '
            f'COUNT(CASE WHEN value = -1 THEN 1 END) AS num_neg_votes, '
            f'COUNT(CASE WHEN value = 0 THEN 1 END) AS num_zero_votes '
            f'FROM personal_votes '
            f'WHERE tg_user_id = %s AND '
            f'(post_id, value) IN (SELECT post_id, value FROM {TMP_PERSONAL_VOTES_TABLE_NAME})'
        )

        DROP_TEMP_TABLE_USER_PERSONAL_VOTES = f'DROP TABLE IF EXISTS {TMP_PERSONAL_VOTES_TABLE_NAME}'

        DROP_TEMP_TABLE_MY_AND_COVOTE_PERSONAL_VOTES = f'DROP TABLE IF EXISTS {TMP_PERSONAL_COVOTES_TABLE_NAME}'


class PostsBase:
    CREATE_POST_BASE = "INSERT INTO posts_base(author, message_id) VALUES (%s, %s) RETURNING id"


class PublicPosts:
    # The purpose of this SQL command is to create a new personal post.
    # The first step is to create an entry in the posts_base table, which includes the author and the message_id.
    # The second step uses a WITH clause to treat the result of the first INSERT statement as a temporary table named
    # new_base.
    # Then we insert a new row into personal_posts table.
    # The new row's post_id corresponds to the id of the newly created base post, and other details are added as well.
    # This operation is atomic, i.e., if any part fails,
    # the entire operation will be rolled back to maintain data consistency.
    CREATE_PUBLIC_POST = (
        # RETURNING id - required in the next insert part of query
        'WITH new_post_base AS (INSERT INTO posts_base(author, message_id) VALUES (%s, %s) RETURNING id) '
        'INSERT INTO public_posts(post_id) '
        # RETURNING id - return finally inserted id
        'SELECT id FROM new_post_base RETURNING post_id'
    )

    READ_PUBLIC_POSTS_IDS = 'SELECT post_id FROM public_posts'

    READ_PUBLIC_POST_PATTERN = (
        'SELECT '
        '    posts_base.author, '
        '    posts_base.message_id, '
        '    public_posts.post_id, '
        '    public_posts.likes_count, '
        '    public_posts.dislikes_count, '
        '    public_posts.status '
        'FROM public_posts '
        'JOIN posts_base ON public_posts.post_id = posts_base.id'
    )

    READ_PUBLIC_POST_BY_ID = f'{READ_PUBLIC_POST_PATTERN} WHERE public_posts.post_id = %s '

    READ_EXCLUSIVE_PUBLIC_POST = (  # Show again if value is 0?
        f'{READ_PUBLIC_POST_PATTERN} '
        'WHERE status = %s AND id NOT IN '
        '(SELECT post_id FROM public_votes WHERE tg_user_id = %s) '
        'ORDER BY created_at DESC LIMIT 1'
    )

    READ_PUBLIC_POSTS_BY_STATUS = f'{READ_PUBLIC_POST_PATTERN} WHERE public_posts.status = %s '

    READ_PUBLIC_POST_MASS = (
        f'{READ_PUBLIC_POST_PATTERN} WHERE status = %s AND release_time IS NULL ORDER BY created_at DESC LIMIT 1'
    )

    UPDATE_PUBLIC_POST_VOTES_COUNT = 'UPDATE public_posts SET likes_count = %s, dislikes_count = %s WHERE post_id = %s'

    UPDATE_PUBLIC_POST_STATUS = 'UPDATE public_posts SET status = %s WHERE post_id = %s'

    DELETE_PUBLIC_POST = 'DELETE FROM public_posts WHERE post_id = %s'


class PersonalPosts:
    # The purpose of this SQL command is to create a new personal post.
    # The first step is to create an entry in the posts_base table, which includes the author and the message_id.
    # The second step uses a WITH clause to treat the result of the first INSERT statement as a temporary table named
    # new_base.
    # Then we insert a new row into personal_posts table.
    # The new row's post_id corresponds to the id of the newly created base post, and other details are added as well.
    # This operation is atomic, i.e., if any part fails,
    # the entire operation will be rolled back to maintain data consistency.
    CREATE_PERSONAL_POST = (
        'WITH new_post_base AS (INSERT INTO posts_base(author, message_id) VALUES (%s, %s) RETURNING id) '
        'INSERT INTO personal_posts(post_id) '
        'SELECT id FROM new_post_base RETURNING post_id'
    )

    READ_PERSONAL_POSTS_PATTERN = (
        'SELECT personal_posts.post_id, posts_base.author, posts_base.message_id FROM personal_posts '
        'JOIN posts_base ON personal_posts.post_id = posts_base.id'
    )

    READ_PERSONAL_POST_BY_ID = f'{READ_PERSONAL_POSTS_PATTERN} WHERE personal_posts.post_id = %s'

    READ_USER_PERSONAL_POSTS = (
        'SELECT posts_base.message_id, personal_posts.post_id FROM personal_posts '
        'JOIN posts_base ON personal_posts.post_id = posts_base.id '
        'WHERE posts_base.author = %s '
    )

    DELETE_PERSONAL_POST = 'DELETE FROM personal_posts WHERE post_id = %s'


class Collections:
    CREATE_COLLECTION = 'INSERT INTO collections (author, name) VALUES (%s, %s) ON CONFLICT DO NOTHING RETURNING id'

    CREATE_M2M_COLLECTIONS_POSTS = (
        'INSERT INTO m2m_collections_posts (collection_id, post_id) VALUES (%s, %s) RETURNING id'
    )

    READ_USER_COLLECTION_ID_BY_NAME = (
        'SELECT id as collection_id FROM collections WHERE author = %s and name = %s LIMIT 1'
    )

    READ_COLLECTIONS_BY_IDS = (  # IN %s - to pass list of values
        'SELECT id as collection_id, author, name FROM collections WHERE id IN %s'
    )

    READ_USER_COLLECTIONS = (
        'SELECT id as collection_id, author, name FROM collections WHERE author = %s'
    )

    READ_PUBLIC_COLLECTION_POSTS = (
        f'{PublicPosts.READ_PUBLIC_POST_PATTERN} WHERE post_id IN '
        f'(SELECT post_id FROM m2m_collections_posts WHERE collection_id = %s)'
    )

    READ_PERSONAL_COLLECTION_POSTS = (
        f'{PersonalPosts.READ_PERSONAL_POSTS_PATTERN} WHERE post_id IN '
        f'(SELECT post_id FROM m2m_collections_posts WHERE collection_id = %s)'
    )

    READ_DEFAULT_COLLECTIONS = f"{READ_USER_COLLECTIONS} and name LIKE %s || '%%'"

    READ_DEFAULT_COLLECTION_NAMES = "SELECT name FROM collections WHERE author = %s and name LIKE %s || '%%'"


class PublicVotes:
    # Not in use
    CREATE_PUBLIC_VOTE = 'INSERT INTO public_votes (tg_user_id, post_id, message_id, value) VALUES (%s, %s, %s, %s)'

    READ_PUBLIC_VOTE = (
        'SELECT tg_user_id, post_id, message_id, value FROM public_votes '
        'WHERE tg_user_id = %s AND post_id = %s'
    )

    READ_USER_PUBLIC_VOTES = 'SELECT tg_user_id, post_id, message_id, value FROM public_votes WHERE tg_user_id = %s'

    READ_USERS_IDS_VOTED_FOR_PUBLIC_POST = "SELECT tg_user_id FROM public_votes WHERE post_id = %s"

    READ_USER_PUBLIC_VOTES_COUNT = 'SELECT COUNT(*) FROM public_votes WHERE tg_user_id = %s'

    UPSERT_PUBLIC_VOTE_VALUE = (  # Not in use
        'INSERT INTO public_votes (tg_user_id, post_id, message_id, value) '
        'VALUES (%s, %s, %s, %s) ON CONFLICT  (tg_user_id, post_id) DO UPDATE SET value = %s'
    )

    UPDATE_PUBLIC_VOTE_VALUE = 'UPDATE public_votes SET value = %s WHERE tg_user_id = %s AND post_id = %s'

    # User may vote only if vote present in DB -  that's condition of app (insertion during sending)
    UPSERT_PUBLIC_VOTE_MESSAGE_ID = (
        'INSERT INTO public_votes (tg_user_id, post_id, message_id) VALUES (%s, %s, %s) '
        'ON CONFLICT (tg_user_id, post_id) DO UPDATE SET message_id = %s'
    )

    DELETE_PUBLIC_VOTE = 'DELETE FROM public_votes WHERE tg_user_id = %s AND post_id = %s'


class PersonalVotes:
    CREATE_PERSONAL_VOTE = (  # Not in use
        'INSERT INTO personal_votes (tg_user_id, post_id, message_id, value) '
        'VALUES (%s, %s, %s, %s)'
    )

    READ_PERSONAL_VOTE = (
        'SELECT tg_user_id, post_id, message_id, value FROM personal_votes '
        'WHERE tg_user_id = %s AND post_id = %s'
    )

    READ_USER_PERSONAL_VOTES = 'SELECT tg_user_id, post_id, message_id, value FROM personal_votes WHERE tg_user_id = %s'

    UPSERT_PERSONAL_VOTE = (
        'INSERT INTO personal_votes (tg_user_id, post_id, message_id, value) '
        'VALUES (%s, %s, %s, %s) '
        'ON CONFLICT (tg_user_id, post_id) DO UPDATE SET message_id = %s, value = %s'
    )

    UPSERT_PERSONAL_VOTE_MESSAGE_ID = (  # Not in use
        'INSERT INTO personal_votes (tg_user_id, post_id, message_id) VALUES (%s, %s, %s) '
        'ON CONFLICT (tg_user_id, post_id) DO UPDATE SET message_id = %s'
    )


class Users:
    CREATE_USER = (
        'INSERT INTO users (tg_user_id, fullname, goal, gender, birthdate, country, city, comment) '
        "VALUES (%s, %s, %s, %s, CURRENT_DATE - INTERVAL '%s YEAR', %s, %s, %s)"
    )

    UPSERT_USER = '''INSERT INTO users (tg_user_id, fullname, goal, gender, birthdate, country, city, comment)
                     VALUES (%s, %s, %s, %s, CURRENT_DATE - INTERVAL '%s YEAR', %s, %s, %s) 
                     ON CONFLICT (tg_user_id) DO UPDATE SET 
                     tg_user_id = %s, fullname = %s, goal = %s, gender = %s, 
                     birthdate = CURRENT_DATE - INTERVAL '%s YEAR', country = %s, city = %s, comment = %s'''

    IS_REGISTERED = 'SELECT 1 from users WHERE tg_user_id = %s'

    READ_USER_PATTERN = (
        "SELECT "
        "fullname, "
        "goal, "
        "gender, "
        # See https://stackoverflow.com/a/40072974/11277611; smallint to convert
        "date_part('year', age(birthdate))::smallint as age, "
        "country, "
        "city, "
        "comment "
        "FROM users"
    )

    READ_USER = f'{READ_USER_PATTERN} WHERE tg_user_id = %s'

    DELETE_USER = 'DELETE FROM users WHERE tg_user_id = %s'


class Photos:
    CREATE_PHOTO = 'INSERT INTO photos (tg_user_id, tg_photo_file_id) VALUES (%s, %s) RETURNING id'

    READ_PHOTOS = 'SELECT tg_photo_file_id FROM photos WHERE tg_user_id = %s'

    DELETE_PHOTO = 'DELETE FROM photos WHERE id = %s'

    DELETE_USER_PHOTOS = 'DELETE FROM photos WHERE tg_user_id = %s'


class ShownUsers:

    CREATE_SHOWN_USER = (
        'INSERT INTO shown_users (tg_user_id, shown_id) VALUES (%s, %s) '
        'ON CONFLICT (tg_user_id, shown_id) DO UPDATE SET created_at=CURRENT_TIMESTAMP'
    )

    # Read inside search query


class System:
    READ_BOTS_IDS = f'SELECT tg_user_id FROM users WHERE tg_user_id < 100 AND comment = %s'
    READ_ALL_USERS_IDS = "SELECT tg_user_id FROM users"


class PostgresSQLS:
    Matches: Type[Matches] = Matches
    PostsBase: Type[PostsBase] = PostsBase
    PublicPosts: Type[PublicPosts] = PublicPosts
    PersonalPosts: Type[PersonalPosts] = PersonalPosts
    Collections: Type[Collections] = Collections
    PublicVotes: Type[PublicVotes] = PublicVotes
    PersonalVotes: Type[PersonalVotes] = PersonalVotes
    Users: Type[Users] = Users
    Photos: Type[Photos] = Photos
    ShownUsers: Type[ShownUsers] = ShownUsers
    System: Type[System] = System

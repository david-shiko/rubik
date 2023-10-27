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

"""Better ro match the table names with the variable names"""

USERS = (
    'CREATE TABLE IF NOT EXISTS users('
    'id serial PRIMARY KEY,'
    'tg_user_id BIGINT NOT NULL UNIQUE,'
    'fullname VARCHAR(64) NOT NULL,'
    'goal INT NOT NULL,'
    'gender INT NOT NULL,'
    'birthdate DATE DEFAULT NULL,'
    'country VARCHAR(64) DEFAULT NULL,'
    'city VARCHAR(64) DEFAULT NULL,'
    'comment VARCHAR(1024) DEFAULT NULL,'
    'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)'
)

PHOTOS = (
    'CREATE TABLE IF NOT EXISTS photos('
    'id serial,'
    'tg_user_id BIGINT,'
    'tg_photo_file_id VARCHAR(512),'
    'FOREIGN KEY (tg_user_id) REFERENCES users (tg_user_id) ON DELETE CASCADE ON UPDATE CASCADE,'
    'UNIQUE (tg_user_id, tg_photo_file_id)'
    ')')

POSTS_BASE = (
    'CREATE TABLE IF NOT EXISTS posts_base('
    'id serial PRIMARY KEY,'
    'author BIGINT NOT NULL,'
    'message_id INT NOT NULL,'
    'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,'
    'updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,'
    'UNIQUE (author, message_id)'
    ')')

TG_POSTS_MAPPING = (  # Introduce me, not in use
    'CREATE TABLE IF NOT EXISTS tg_posts_mapping('
    'post_id INT PRIMARY KEY,'
    'tg_message_id INT NOT NULL,'
    'FOREIGN KEY (post_id) REFERENCES posts_base (id) ON DELETE CASCADE ON UPDATE CASCADE,'
    'UNIQUE (post_id, tg_message_id)'
    ')'
)

PUBLIC_POSTS = (
    'CREATE TABLE IF NOT EXISTS public_posts('
    'post_id INT PRIMARY KEY,'
    'likes_count INTEGER NOT NULL DEFAULT 0,'
    'dislikes_count INTEGER NOT NULL DEFAULT 0,'
    'status INT DEFAULT 0,'
    'release_time TIMESTAMP DEFAULT NULL,'
    'FOREIGN KEY (post_id) REFERENCES posts_base (id) ON DELETE CASCADE ON UPDATE CASCADE'
    ')')

PERSONAL_POSTS = (
    'CREATE TABLE IF NOT EXISTS personal_posts('
    'post_id INT PRIMARY KEY,'
    'FOREIGN KEY (post_id) REFERENCES posts_base (id) ON DELETE CASCADE ON UPDATE CASCADE'
    ')')

COLLECTIONS = (
    'CREATE TABLE IF NOT EXISTS collections('
    'id serial PRIMARY KEY,'
    'author BIGINT NOT NULL,'
    'name VARCHAR(64) NOT NULL,'
    'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,'
    'updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,'
    'UNIQUE (author, name)'
    ')')

M2M_COLLECTIONS_POSTS = (
    'CREATE TABLE IF NOT EXISTS m2m_collections_posts('
    'id serial PRIMARY KEY,'
    'collection_id INT NOT NULL,'
    'post_id INT NOT NULL,'
    'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,'
    'updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,'
    'FOREIGN KEY (post_id) REFERENCES posts_base (id) ON UPDATE CASCADE ON DELETE CASCADE,'
    'FOREIGN KEY (collection_id) REFERENCES collections (id) ON UPDATE CASCADE ON DELETE CASCADE, '
    'UNIQUE (collection_id, post_id)'  # What if user wants to put the same post multiple times in the collection ?
    ')')

VOTES_BASE_COLUMNS = (
    'id serial,'
    'tg_user_id BIGINT,'
    'post_id INTEGER,'
    'message_id INTEGER NOT NULL,'
    'value INTEGER DEFAULT NULL,'
    'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,'
    'updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,'
    'PRIMARY KEY (tg_user_id, post_id),'
)

# Maybe no need to delete likes for people if post was deleted, anyway match is occurred?
PUBLIC_VOTES = (
    f'CREATE TABLE IF NOT EXISTS public_votes({VOTES_BASE_COLUMNS}'
    'FOREIGN KEY (post_id) REFERENCES public_posts (post_id) ON DELETE CASCADE ON UPDATE CASCADE'
    ')')

PERSONAL_VOTES = (
    f'CREATE TABLE IF NOT EXISTS personal_votes({VOTES_BASE_COLUMNS}'
    'FOREIGN KEY (post_id) REFERENCES personal_posts (post_id) ON DELETE CASCADE ON UPDATE CASCADE'
    ')')

SHOWN_USERS = (
    'CREATE TABLE IF NOT EXISTS shown_users ('
    'id serial,'
    'tg_user_id BIGINT,'
    'shown_id BIGINT,'
    'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,'
    'PRIMARY KEY (tg_user_id, shown_id),'
    'FOREIGN KEY (tg_user_id) REFERENCES users (tg_user_id) ON DELETE CASCADE ON UPDATE CASCADE,'
    'FOREIGN KEY (shown_id) REFERENCES users (tg_user_id) ON DELETE CASCADE ON UPDATE CASCADE,'
    'UNIQUE (tg_user_id, shown_id)'
    ')')

TABLES = (
    USERS,
    PHOTOS,
    POSTS_BASE,
    PUBLIC_POSTS,
    PERSONAL_POSTS,
    COLLECTIONS,
    M2M_COLLECTIONS_POSTS,
    PUBLIC_VOTES,
    PERSONAL_VOTES,
    SHOWN_USERS,
)

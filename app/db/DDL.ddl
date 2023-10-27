CREATE TABLE IF NOT EXISTS users
(
    id         serial PRIMARY KEY,
    tg_user_id BIGINT      NOT NULL UNIQUE,
    fullname   VARCHAR(64) NOT NULL,
    goal       INT         NOT NULL,
    gender     INT         NOT NULL,
    birthdate  DATE          DEFAULT NULL,
    country    VARCHAR(64)   DEFAULT NULL,
    city       VARCHAR(64)   DEFAULT NULL,
    comment    VARCHAR(1024) DEFAULT NULL,
    created_at TIMESTAMP     DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS photos
(
    id               serial,
    tg_user_id       BIGINT,
    tg_photo_file_id VARCHAR(512),
    FOREIGN KEY (tg_user_id) REFERENCES users (tg_user_id) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE TABLE IF NOT EXISTS public_posts
(
    id             serial PRIMARY KEY,
    author         BIGINT           DEFAULT 838004799,
    message_id     INT     NOT NULL,
    likes_count    INTEGER NOT NULL DEFAULT 0,
    dislikes_count INTEGER NOT NULL DEFAULT 0,
    status         INT              DEFAULT 0,
    created_at     TIMESTAMP        DEFAULT CURRENT_TIMESTAMP,
    release_time   TIMESTAMP        DEFAULT NULL,
    FOREIGN KEY (author) REFERENCES users (tg_user_id) ON UPDATE CASCADE ON DELETE SET DEFAULT
);


CREATE TABLE IF NOT EXISTS personal_posts
(
    id         serial PRIMARY KEY,
    author     BIGINT,
    message_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author) REFERENCES users (tg_user_id) ON UPDATE CASCADE ON DELETE SET NULL
);


CREATE TABLE IF NOT EXISTS public_votes
(
    id         serial,
    tg_user_id BIGINT,
    post_id    INTEGER,
    message_id INTEGER NOT NULL,
    value      INTEGER   DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (tg_user_id, post_id),
    FOREIGN KEY (tg_user_id) REFERENCES users (tg_user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (post_id) REFERENCES public_posts (id) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE TABLE IF NOT EXISTS personal_votes
(
    id         serial,
    tg_user_id BIGINT,
    post_id    INTEGER,
    value      INTEGER   DEFAULT NULL,
    message_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (tg_user_id, post_id),
    FOREIGN KEY (tg_user_id) REFERENCES users (tg_user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (post_id) REFERENCES personal_posts (id) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE TABLE IF NOT EXISTS personal_votes_messages
(
    id         serial,
    post_id    INTEGER,
    sender     BIGINT  NOT NULL,
    recipient  BIGINT  NOT NULL,
    message_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (sender, recipient, message_id),
    FOREIGN KEY (post_id, sender) REFERENCES personal_votes (tg_user_id, post_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (post_id, recipient) REFERENCES personal_votes (tg_user_id, post_id) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE TABLE IF NOT EXISTS shown_users
(
    id         serial,
    tg_user_id BIGINT,
    shown_id   BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (tg_user_id, shown_id),
    FOREIGN KEY (tg_user_id) REFERENCES users (tg_user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (shown_id) REFERENCES users (tg_user_id) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE TABLE IF NOT EXISTS user_votes
(
    post_id INTEGER,
    value   INTEGER
);


CREATE TABLE IF NOT EXISTS user_covotes
(
    tg_user_id             BIGINT PRIMARY KEY,
    count_common_interests INTEGER
);


CREATE TABLE IF NOT EXISTS user_personal_votes
(
    post_id INTEGER,
    value   INTEGER
);


CREATE TABLE IF NOT EXISTS my_and_covote_personal_votes
(
    tg_user_id BIGINT,
    post_id    INTEGER,
    value      INTEGER
);


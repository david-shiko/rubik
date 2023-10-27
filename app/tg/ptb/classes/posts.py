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
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, TypeVar, Type
from dataclasses import dataclass

# noinspection PyPackageRequirements
from telegram import InlineKeyboardMarkup as tg_IKM, InlineKeyboardButton as tg_IKB
# noinspection PyPackageRequirements
from telegram.error import BadRequest, TimedOut, Unauthorized

import app.exceptions
import app.models.base.posts

import app.tg.classes.posts

from app.tg import ptb
import app.tg.ptb.config

if TYPE_CHECKING:
    # noinspection PyPackageRequirements
    from telegram import CallbackQuery, MessageId, Message
    from psycopg2.extensions import connection as pg_ext_connection
    import app.models.users
    import app.tg.ptb.classes.votes
    import app.structures.type_hints

PostBaseType = TypeVar('PostBaseType', bound='PostBase')

"""
SCHEME:

PostBase -> BotPostBase, ChannelPublicPost
BotPostBase -> BotPublicPost, PublicPost, PersonalPost  # BotPersonalPost?

Final: BotPublicPost, PublicPost, PersonalPost  # BotPersonalPost?
"""


class PostBase(ABC, ):
    @classmethod
    def callback_to_post(
            cls: Type[PostBaseType],
            callback: CallbackQuery,
            connection: pg_ext_connection,
    ) -> PostBaseType:
        """Interface to read a full post by incoming id"""
        post_id = abs(int(callback.data.split()[-1]))
        post = cls.read(post_id=post_id, connection=connection, )
        if post:
            return post
        else:
            raise app.exceptions.PostNotFound


class BotPostBase(PostBase, app.models.base.posts.PostProtocol, ):
    """Bot Post is post intended to be used inside bot (not a post channel). It's public or private post"""
    POS_EMOJI: str  # Depend on the post type
    NEG_EMOJI: str  # Depend on the post type
    MARK_VOTE: str  # Depend on the post type

    @staticmethod
    def remove_old_user_post(
            tg_user_id: int,
            message_id: int | None,  # None - if old post not found in db
    ) -> bool | None:
        """Remove old user post if the same one was sent again"""
        if message_id is not None:  # Delete old posts (messages) from recipient chat before send
            try:
                return ptb.config.Config.bot.delete_message(chat_id=tg_user_id, message_id=message_id)
            except (BadRequest, Unauthorized, TimedOut):  # If message not found
                pass  # TODO behavior
        return None

    def _get_keyboard(
            self,
            clicker_vote: app.tg.ptb.classes.votes.PublicVote | app.tg.ptb.classes.votes.PersonalVote,
            pattern: str,
    ) -> tg_IKM:
        """
        Keyboard to display user vote (not for a posts forms, they are uses another keyboard).
        """
        pos_btn_text = self.POS_EMOJI
        neg_btn_text = self.NEG_EMOJI

        if clicker_vote.value == clicker_vote.Value.POSITIVE:  # Use vote.is_positive / vote.is_negative
            pos_btn_text += self.MARK_VOTE
        elif clicker_vote.value == clicker_vote.Value.NEGATIVE:
            neg_btn_text += self.MARK_VOTE
        return tg_IKM(
            [[
                tg_IKB(text=neg_btn_text, callback_data=f'{pattern} {clicker_vote.user.tg_user_id} -{self.post_id}', ),
                tg_IKB(text=pos_btn_text, callback_data=f'{pattern} {clicker_vote.user.tg_user_id} +{self.post_id}', ),
            ]]
        )


class BotPublicPostInterface(app.tg.classes.posts.BotPublicPostInterface, ):
    """Bot Post is post intended to be used inside bot (not a post channel). It's public or private post"""

    @staticmethod
    @abstractmethod
    def remove_old_user_post(tg_user_id: int, message_id: int | None, ) -> bool:  # None - if old post not found in db
        """Remove old user post if the same one was sent again"""
        ...

    @abstractmethod
    def get_keyboard(self, clicker_vote: app.tg.ptb.classes.votes.PublicVote, ) -> tg_IKM:
        """
        Interactive keyboard to graphically (by emojy) show simultaneously two votes (sender and recipient).
        In cbk button data only opposite tg_user_id (clicker accessible from update)
        """
        ...

    @abstractmethod
    def update_poll_keyboard(
            self,
            clicker_vote: app.tg.ptb.classes.votes.PublicVote,
            pattern: str = ptb.config.PUBLIC_VOTE_CBK_S,
    ) -> Message:
        ...


class BotPublicPost(BotPostBase, app.tg.classes.posts.BotPublicPost, BotPublicPostInterface, ):
    """Bot Post is post intended to be used inside bot (not a post channel). It's public or private post"""

    def get_keyboard(self, clicker_vote: app.tg.ptb.classes.votes.PublicVote, ) -> tg_IKM:
        """
        Interactive keyboard to graphically (by emojy) show simultaneously two votes (sender and recipient).
        In cbk button data only opposite tg_user_id (clicker accessible from update)
        """
        return super()._get_keyboard(clicker_vote=clicker_vote, pattern=ptb.config.PUBLIC_VOTE_CBK_S, )

    def get_keyboard_deprecated(self, ) -> tg_IKM:
        """
        This is keyboard for appending to the post and voting.
        TG can accept only str callback data. Like = +post_id, dislike = -post_id.
        """
        return tg_IKM(
            [[
                tg_IKB(
                    text=f'{self.NEG_EMOJI} {self.dislikes_count}',
                    callback_data=f'{ptb.config.PUBLIC_VOTE_CBK_S} -{self.post_id}'
                ),
                tg_IKB(
                    text=f'{self.POS_EMOJI} {self.likes_count}',
                    callback_data=f'{ptb.config.PUBLIC_VOTE_CBK_S} +{self.post_id}'
                ),
            ]]
        )

    def update_poll_keyboard(
            self,
            clicker_vote: app.tg.ptb.classes.votes.PublicVote,
            pattern: str = ptb.config.PUBLIC_VOTE_CBK_S,
    ) -> Message:
        return ptb.config.Config.bot.edit_message_reply_markup(
            chat_id=clicker_vote.user.tg_user_id,
            # message_id=message_id or self.message_id,
            message_id=clicker_vote.message_id,
            reply_markup=self.get_keyboard(clicker_vote=clicker_vote, ),
        )


class PublicPostInterface(app.tg.classes.posts.PublicPostInterface, ABC, ):

    class Keyboards(ABC, ):
        class ShowPending(ABC, ):
            BTN_1: app.constants.Posts.Public.Buttons.PENDING
            BTN_2: app.constants.Posts.Public.Buttons.READY_TO_RELEASE

            @staticmethod
            def build_cbk(post: PublicPostInterface, status: PublicPostInterface.Status, ): ...

            @classmethod
            def update_status(cls, post: PublicPostInterface, ) -> tg_IKM: ...

    @classmethod
    @abstractmethod
    def callback_to_post(cls, callback: CallbackQuery, connection: pg_ext_connection) -> PublicPostInterface:
        ...

    @abstractmethod
    def send(self, clicker_vote: app.tg.ptb.classes.votes.PublicVoteInterface, ) -> MessageId:
        ...

    @abstractmethod
    def get_keyboard(self, clicker_vote: app.tg.ptb.classes.votes.PublicVoteInterface, ) -> tg_IKM:
        """
        Interactive keyboard to graphically (by emojy) show simultaneously two votes (sender and recipient).
        In cbk button data only opposite tg_user_id (clicker accessible from update)
        """
        ...

    @abstractmethod
    def get_keyboard_deprecated(self, ) -> tg_IKM:
        """
        Interactive keyboard to graphically (by emojy) show simultaneously two votes (sender and recipient).
        In cbk button data only opposite tg_user_id (clicker accessible from update)
        """
        ...


class PublicPost(BotPostBase, app.tg.classes.posts.PublicPost, PublicPostInterface, ):
    """
    Public post don't have keyboard cuz in depend on target chat (bot or channel)
    """
    Mapper: ptb.classes.PublicPostMapper

    def send(self, clicker_vote: app.tg.ptb.classes.votes.PublicVoteInterface, ) -> MessageId:
        return ptb.config.Config.bot.copy_message(
            chat_id=clicker_vote.user.tg_user_id,
            from_chat_id=self.STORE_CHANNEL_ID,
            message_id=self.message_id,
            reply_markup=self.get_keyboard(clicker_vote=clicker_vote, ),
        )

    def get_keyboard(self, clicker_vote: app.tg.ptb.classes.votes.PublicVoteInterface, ) -> tg_IKM:
        """
        Interactive keyboard to graphically (by emojy) show simultaneously two votes (sender and recipient).
        In cbk button data only opposite tg_user_id (clicker accessible from update)
        """
        return super()._get_keyboard(clicker_vote=clicker_vote, pattern=ptb.config.PUBLIC_VOTE_CBK_S, )

    def get_keyboard_deprecated(self, ) -> tg_IKM:
        """
        Interactive keyboard to graphically (by emojy) show simultaneously two votes (sender and recipient).
        In cbk button data only opposite tg_user_id (clicker accessible from update)
        """
        return tg_IKM(
            [[
                tg_IKB(text=self.POS_EMOJI, callback_data=f'{ptb.config.PUBLIC_VOTE_CBK_S} -{self.post_id}', ),
                tg_IKB(text=self.NEG_EMOJI, callback_data=f'{ptb.config.PUBLIC_VOTE_CBK_S} +{self.post_id}', ),
            ]]
        )

    class Keyboards(PublicPostInterface.Keyboards, ):
        class ShowPending(PublicPostInterface.Keyboards.ShowPending, ):
            BTN_1 = app.constants.Posts.Public.Buttons.PENDING
            BTN_2 = app.constants.Posts.Public.Buttons.READY_TO_RELEASE

            @staticmethod
            def build_cbk(post: PublicPostInterface, status: PublicPostInterface.Status, ):
                return f'{app.tg.ptb.config.UPDATE_PUBLIC_POST_STATUS_CBK_S} {post.post_id} {status}'

            @classmethod
            def update_status(cls, post: PublicPostInterface, ) -> tg_IKM:
                return tg_IKM(
                    [[
                        tg_IKB(
                            text=cls.BTN_1,
                            callback_data=cls.build_cbk(post=post, status=post.Status.PENDING, ),
                        ),
                        tg_IKB(
                            text=cls.BTN_2,
                            callback_data=cls.build_cbk(post=post, status=post.Status.READY_TO_RELEASE, ),
                        ),
                    ]]
                )


class ChannelPublicPost(app.tg.classes.posts.PublicPost, PostBase):

    def get_keyboard(self, pattern: str = ptb.config.CHANNEL_PUBLIC_VOTE_CBK_S, ) -> tg_IKM:
        """
        This is keyboard for appending to the post and voting.
        TG can accept only str callback data
        """
        return tg_IKM(  # Use regular keyboard?
            [[
                tg_IKB(text=f'{self.NEG_EMOJI} {self.dislikes_count}', callback_data=f'{pattern} -{self.post_id}'),
                tg_IKB(text=f'{self.POS_EMOJI} {self.likes_count}', callback_data=f'{pattern} +{self.post_id}'),
            ]]
        )

    def update_poll_keyboard(self, message_id: int, ) -> Message:
        return ptb.config.Config.bot.edit_message_reply_markup(
            chat_id=self.POSTS_CHANNEL_ID,
            message_id=message_id,  # just post.message_id - is store channel message_id
            reply_markup=self.get_keyboard(),
        )

    def show(self, ) -> MessageId:
        """show the same as send (send reviewed and deprecated) """
        return ptb.config.Config.bot.copy_message(
            chat_id=self.POSTS_CHANNEL_ID,
            from_chat_id=self.STORE_CHANNEL_ID,
            message_id=self.message_id,
            reply_markup=self.get_keyboard(),
        )


class BotPersonalPostInterface(app.tg.classes.posts.BotPersonalPostInterface, ABC):
    """Bot Post is post intended to be used inside bot (not a post channel). It's public or private post"""
    MARK_VOTE: str

    @abstractmethod
    def get_keyboard(
            self,
            clicker_vote: app.tg.ptb.classes.votes.PersonalVote,
            pattern: str = ptb.config.PERSONAL_VOTE_CBK_S,
    ) -> tg_IKM:
        """
        Interactive keyboard to graphically (by emojy) show simultaneously two votes (sender and recipient).
        In cbk button data only opposite tg_user_id (clicker accessible from update)
        """
        ...


class BotPersonalPost(BotPostBase, app.tg.classes.posts.BotPersonalPost, BotPersonalPostInterface, ):
    """Bot Post is post intended to be used inside bot (not a post channel). It's public or private post"""
    MARK_VOTE: str

    def get_keyboard(
            self,
            clicker_vote: app.tg.ptb.classes.votes.PersonalVoteInterface,
            pattern: str = ptb.config.PERSONAL_VOTE_CBK_S,
    ) -> tg_IKM:
        """
        Interactive keyboard to graphically (by emojy) show simultaneously two votes (sender and recipient).
        In cbk button data only opposite tg_user_id (clicker accessible from update)
        """
        return super()._get_keyboard(clicker_vote=clicker_vote, pattern=pattern, )


class PersonalPostInterface(app.tg.classes.posts.PersonalPostInterface, ABC, ):
    @classmethod
    @abstractmethod
    def extract_cbk_data(cls, callback_data: str) -> tuple[app.models.users.User, bool]:
        ...

    @classmethod
    @abstractmethod
    def callback_to_post(cls, callback: CallbackQuery, connection: pg_ext_connection) -> PersonalPostInterface:
        ...

    @abstractmethod
    def get_keyboard(
            self,
            clicker_vote: app.tg.ptb.classes.votes.PersonalVote,
            opposite_vote: app.tg.ptb.classes.votes.PersonalVote,
            pattern: str = ptb.config.PERSONAL_VOTE_CBK_S,
    ) -> tg_IKM:
        ...

    @abstractmethod
    def update_poll_keyboard(
            self,
            clicker_vote: app.tg.ptb.classes.votes.PersonalVote,
            opposite_vote: app.tg.ptb.classes.votes.PersonalVote,
    ) -> Message | bool:
        ...


class PersonalPost(app.tg.classes.posts.PersonalPost, BotPostBase, PersonalPostInterface, ):
    Mapper: ptb.classes.PersonalPostMapper

    @classmethod
    def extract_cbk_data(cls, callback_data: str, ) -> tuple[app.models.users.User, bool]:
        """
        Get payload of callback
        Not a part of logic (domain) object
        """
        _, str_recipient_tg_user_id, flag = callback_data.split()
        return cls.Mapper.User(tg_user_id=int(str_recipient_tg_user_id)), bool(int(flag))

    def send(
            self,
            clicker_vote: app.tg.ptb.classes.votes.PersonalVote,
            opposite_vote: app.tg.ptb.classes.votes.PersonalVote,
    ) -> MessageId:
        return ptb.config.Config.bot.copy_message(
            chat_id=clicker_vote.user.tg_user_id,
            from_chat_id=self.STORE_CHANNEL_ID,
            message_id=self.message_id,
            reply_markup=self.get_keyboard(
                clicker_vote=clicker_vote,
                opposite_vote=opposite_vote,
            ),
        )

    def get_keyboard(
            self,
            clicker_vote: app.tg.ptb.classes.votes.PersonalVote,
            opposite_vote: app.tg.ptb.classes.votes.PersonalVote,
            pattern: str = ptb.config.PERSONAL_VOTE_CBK_S,
    ) -> tg_IKM:
        """
        Interactive keyboard to graphically (by emojy) show simultaneously two votes (sender and recipient).
        In cbk button data only opposite tg_user_id (clicker accessible from update)
        """
        pos_btn_text = neg_btn_text = ''  # Use str builder

        if clicker_vote.value == clicker_vote.Value.POSITIVE:
            pos_btn_text += f'{self.POS_EMOJI}{self.MARK_VOTE}'
        elif clicker_vote.value == clicker_vote.Value.NEGATIVE:
            neg_btn_text += f'{self.NEG_EMOJI}{self.MARK_VOTE}'

        if opposite_vote.value == clicker_vote.Value.POSITIVE:
            pos_btn_text += self.POS_EMOJI
        elif opposite_vote.value == clicker_vote.Value.NEGATIVE:
            neg_btn_text += self.NEG_EMOJI

        # opposite - see docstring; {{}} - for future format;
        cbk = f'{pattern} {opposite_vote.user.tg_user_id} {{}}{self.post_id}'
        return tg_IKM(
            [[
                tg_IKB(text=neg_btn_text or self.DISLIKE, callback_data=cbk.format('-')),
                tg_IKB(text=pos_btn_text or self.LIKE, callback_data=cbk.format('+')),
            ]]
        )

    def share(
            self,
            post_sender: app.models.users.User,
            post_recipient: app.models.users.User,
    ) -> Exception | None:
        """Share post from one user to another (send the same post simultaneous;y to 2 users)"""
        post_sender_vote: app.tg.ptb.classes.votes.PersonalVote = post_sender.get_vote(post=self, )
        post_recipient_vote: app.tg.ptb.classes.votes.PersonalVote = post_recipient.get_vote(post=self, )
        self.remove_old_user_post(tg_user_id=post_sender.tg_user_id, message_id=post_sender_vote.message_id, )
        self.remove_old_user_post(tg_user_id=post_recipient.tg_user_id, message_id=post_recipient_vote.message_id, )
        try:
            # send message to me
            sender_sent_message = self.send(
                clicker_vote=post_sender_vote,
                opposite_vote=post_recipient_vote,
            )
            # send message to opposite user
            recipient_sent_message = self.send(
                clicker_vote=post_recipient_vote,
                opposite_vote=post_sender_vote,
            )
        except (Unauthorized, BadRequest) as e:
            ptb.config.Config.logger.error(e)
            return e
        # Upsert sent message to me
        post_sender_vote.upsert(message_id=sender_sent_message.message_id, )
        # Upsert sent message to opposite user
        post_recipient_vote.upsert(message_id=recipient_sent_message.message_id, )

    def update_poll_keyboard(
            self,
            clicker_vote: app.tg.ptb.classes.votes.PersonalVote,
            opposite_vote: app.tg.ptb.classes.votes.PersonalVote,
    ) -> Message | bool:
        return ptb.config.Config.bot.edit_message_reply_markup(
            chat_id=clicker_vote.user.tg_user_id,
            message_id=clicker_vote.message_id,
            reply_markup=self.get_keyboard(
                clicker_vote=clicker_vote,
                opposite_vote=opposite_vote,
            ), )


class VotedPublicPostInterface(app.tg.classes.posts.VotedPersonalPostInterface, ABC, ):
    post: PersonalPost
    clicker_vote: PersonalPost.Mapper.Vote

    @abstractmethod
    def send(self, ) -> MessageId:
        ...


@dataclass
class VotedPublicPost(app.tg.classes.posts.VotedPublicPost, VotedPublicPostInterface, ):
    post: PublicPostInterface
    clicker_vote: PublicPost.Mapper.Vote

    def send(self, ) -> MessageId:
        return self.post.send(clicker_vote=self.clicker_vote, )


@dataclass
class VotedPersonalPostInterface(app.tg.classes.posts.VotedPersonalPostInterface, ABC, ):
    post: PersonalPost
    clicker_vote: PersonalPost.Mapper.Vote
    opposite_vote: PersonalPost.Mapper.Vote

    @abstractmethod
    def send(self, ) -> MessageId:
        ...


@dataclass
class VotedPersonalPost(app.tg.classes.posts.VotedPersonalPost, VotedPersonalPostInterface, ):
    post: PersonalPost
    clicker_vote: PersonalPost.Mapper.Vote
    opposite_vote: PersonalPost.Mapper.Vote

    def send(self, ) -> MessageId:
        return ptb.config.Config.bot.copy_message(
            chat_id=self.clicker_vote.user.tg_user_id,
            from_chat_id=self.post.STORE_CHANNEL_ID,
            message_id=self.post.message_id,
            reply_markup=self.post.get_keyboard(
                clicker_vote=self.clicker_vote,
                opposite_vote=self.opposite_vote,
            ),
        )

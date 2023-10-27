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
from typing import TYPE_CHECKING, Callable

# noinspection PyPackageRequirements
from telegram import Update
# noinspection PyPackageRequirements
from telegram.ext import (
    Dispatcher,
    TypeHandler,
    Filters,
    MessageHandler,
    CallbackQueryHandler,
    CommandHandler,
)

from app.config import MAIN_ADMIN, ADMINS
from app.tg.ptb import config, constants, handlers as ptb_handlers

from custom_ptb.conversation_handler import ConversationHandler

if TYPE_CHECKING:
    from app.tg.ptb.structures import DispatcherAddHandlerKwargs

"""
1. https://stackoverflow.com/a/61275118/11277611
2. Value in seconds for dropping db connection and user temporary tables
"""

DEFAULT_CH_TIMEOUT = 18000


def create_cancel():
    cancel = MessageHandler(
        filters=Filters.regex(constants.Regexp.CANCEL_R),
        callback=ptb_handlers.mix.cancel,
    )
    return cancel


class PersonalScenarioCH:

    @staticmethod
    def create_entry_point():
        entry_point = CommandHandler(
            command=config.PERSONAL_SCENARIO_S,
            callback=ptb_handlers.start.PersonalScenario.entry_point,
        )
        return entry_point

    @staticmethod
    def create_show_collections_cbk_handler():
        """Show all collections and set cbk to mark some of them"""
        show_collections_handler = CallbackQueryHandler(
            callback=ptb_handlers.start.PersonalScenario.show_collection_posts_for_sender_cbk_handler,
            pattern=config.MARK_SHOW_COLLECTION_CBK_R,
        )
        return show_collections_handler

    @staticmethod
    def create_continue_handler():
        continue_handler = MessageHandler(
            filters=Filters.text,
            callback=ptb_handlers.collections.SharePersonalCollections.continue_handler,
        )
        return continue_handler

    @staticmethod
    def create_recipient_handler():
        recipient_handler = MessageHandler(
            filters=Filters.text,
            callback=ptb_handlers.collections.SharePersonalCollections.recipient_handler,
        )
        return recipient_handler

    entry_point = create_entry_point()
    cancel = create_cancel()
    show_collections_cbk_handler = create_show_collections_cbk_handler()
    recipient_handler = create_recipient_handler()
    continue_handler = create_continue_handler()
    CH = None

    @classmethod
    def create_ch(cls, set_ch: bool = True, ) -> ConversationHandler:
        result = ConversationHandler(
            entry_points=[cls.entry_point, ],
            prefallbacks=[cls.cancel, ],
            states={
                0: [cls.show_collections_cbk_handler, cls.continue_handler, ],
                1: [cls.recipient_handler, ],
                ConversationHandler.TIMEOUT: [TypeHandler(type=Update, callback=cls.cancel.callback, )]  # See 1
            },
            fallbacks=[],
            conversation_timeout=DEFAULT_CH_TIMEOUT,
            allow_reentry=True,
            name='personal_scenario'
        )
        if set_ch is True:
            cls.CH = result
        return result


class RegistrationCH:
    @staticmethod
    def create_entry_point():
        entry_point = CommandHandler(
            command=config.REG_S,
            callback=ptb_handlers.reg.entry_point,
        )
        return entry_point

    @staticmethod
    def create_entry_point_handler():
        entry_point_handler = MessageHandler(
            filters=Filters.text,
            callback=ptb_handlers.reg.entry_point_handler,
        )
        return entry_point_handler

    @staticmethod
    def create_name_handler():
        name_handler = MessageHandler(
            filters=Filters.text,
            callback=ptb_handlers.reg.name_handler,
        )
        return name_handler

    @staticmethod
    def create_goal_handler():
        goal_handler = MessageHandler(
            filters=Filters.text,
            callback=ptb_handlers.reg.goal_handler,
        )
        return goal_handler

    @staticmethod
    def create_gender_handler():
        gender_handler = MessageHandler(
            filters=Filters.text,
            callback=ptb_handlers.reg.gender_handler,
        )
        return gender_handler

    @staticmethod
    def create_age_handler():
        age_handler = MessageHandler(
            filters=Filters.text,
            callback=ptb_handlers.reg.age_handler,
        )
        return age_handler

    @staticmethod
    def create_location_handler_geo():
        location_handler_geo = MessageHandler(
            filters=Filters.location,
            callback=ptb_handlers.reg.location_handler_geo,
        )
        return location_handler_geo

    @staticmethod
    def create_location_handler_text():
        location_handler_text = MessageHandler(
            filters=Filters.text,
            callback=ptb_handlers.reg.location_handler_text,
        )
        return location_handler_text

    @staticmethod
    def create_photos_handler_photo():
        photos_handler_tg_photo = MessageHandler(
            filters=Filters.photo,
            callback=ptb_handlers.reg.photos_handler_tg_photo,
        )
        return photos_handler_tg_photo

    @staticmethod
    def create_photos_handler_text():
        photos_handler_text = MessageHandler(
            filters=Filters.text,
            callback=ptb_handlers.reg.photos_handler_text,
        )
        return photos_handler_text

    @staticmethod
    def create_comment_handler():
        comment_handler = MessageHandler(
            filters=Filters.text,
            callback=ptb_handlers.reg.comment_handler,
        )
        return comment_handler

    @staticmethod
    def create_confirm_handler():
        confirm_handler = MessageHandler(
            filters=Filters.text,
            callback=ptb_handlers.reg.confirm_handler,
        )
        return confirm_handler

    entry_point = create_entry_point()
    cancel = create_cancel()
    entry_point_handler = create_entry_point_handler()
    name_handler = create_name_handler()
    goal_handler = create_goal_handler()
    gender_handler = create_gender_handler()
    age_handler = create_age_handler()
    location_handler_geo = create_location_handler_geo()
    location_handler_text = create_location_handler_text()
    photos_handler_photo = create_photos_handler_photo()
    photos_handler_text = create_photos_handler_text()
    comment_handler = create_comment_handler()
    confirm_handler = create_confirm_handler()
    CH: ConversationHandler = None

    @classmethod
    def create_ch(cls, set_ch: bool = True, ) -> ConversationHandler:
        result = ConversationHandler(
            entry_points=[cls.entry_point],

            prefallbacks=[cls.cancel, ],
            states={
                0: [cls.entry_point_handler, ],
                1: [cls.name_handler, ],
                2: [cls.goal_handler, ],
                3: [cls.gender_handler, ],
                4: [cls.age_handler, ],
                5: [cls.location_handler_geo, cls.location_handler_text],
                6: [cls.photos_handler_photo, cls.photos_handler_text, ],
                7: [cls.comment_handler],
                8: [cls.confirm_handler],
                ConversationHandler.TIMEOUT: [TypeHandler(type=Update, callback=cls.cancel.callback, )]  # See 1
            },
            fallbacks=[],
            conversation_timeout=DEFAULT_CH_TIMEOUT,  # See 2
            allow_reentry=True,
            name='registration'
        )
        if set_ch is True:
            cls.CH = result
        return result


class SearchCH:

    @staticmethod
    def create_entry_point():
        entry_point = CommandHandler(
            command=config.SEARCH_S,
            callback=ptb_handlers.search.entry_point,
        )
        return entry_point

    @staticmethod
    def create_entry_point_handler():
        entry_point_handler = MessageHandler(
            filters=Filters.text,
            callback=ptb_handlers.search.entry_point_handler,
        )
        return entry_point_handler

    @staticmethod
    def create_goal_handler():
        goal_handler = MessageHandler(
            filters=Filters.text,
            callback=ptb_handlers.search.goal_handler,
        )
        return goal_handler

    @staticmethod
    def create_gender_handler():
        gender_handler = MessageHandler(
            filters=Filters.text,
            callback=ptb_handlers.search.gender_handler,
        )
        return gender_handler

    @staticmethod
    def create_age_handler():
        age_handler = MessageHandler(
            filters=Filters.text,
            callback=ptb_handlers.search.age_handler,
        )
        return age_handler

    @staticmethod
    def create_checkbox_cbk_handler():
        checkbox_cbk_handler = CallbackQueryHandler(
            callback=ptb_handlers.search.checkbox_cbk_handler,
            pattern=config.CHECKBOX_CBK_R,
        )
        return checkbox_cbk_handler

    @staticmethod
    def create_checkboxes_handler():
        checkboxes_handler = MessageHandler(
            filters=Filters.text,
            callback=ptb_handlers.search.checkboxes_handler,
        )
        return checkboxes_handler

    @staticmethod
    def create_confirm_handler():
        confirm_handler = MessageHandler(
            filters=Filters.text,
            callback=ptb_handlers.search.match_type_handler,
        )
        return confirm_handler

    @staticmethod
    def create_show_match_handler():
        show_match_handler = MessageHandler(
            filters=Filters.text,
            callback=ptb_handlers.search.show_match_handler,
        )
        return show_match_handler

    entry_point = create_entry_point()
    cancel = create_cancel()
    entry_point_handler = create_entry_point_handler()
    goal_handler = create_goal_handler()
    gender_handler = create_gender_handler()
    age_handler = create_age_handler()
    checkbox_cbk_handler = create_checkbox_cbk_handler()
    checkboxes_handler = create_checkboxes_handler()
    confirm_handler = create_confirm_handler()
    show_match_handler = create_show_match_handler()
    CH: ConversationHandler = None

    @classmethod
    def create_ch(cls, set_ch: bool = True, ) -> ConversationHandler:
        result = ConversationHandler(
            entry_points=[cls.entry_point, ],
            prefallbacks=[cls.cancel, ],
            states={
                0: [cls.entry_point_handler, ],
                1: [cls.goal_handler, ],
                2: [cls.gender_handler, ],
                3: [cls.age_handler, ],
                4: [cls.checkbox_cbk_handler, cls.checkboxes_handler, ],
                5: [cls.confirm_handler, ],
                6: [cls.show_match_handler, ],
                ConversationHandler.TIMEOUT: [TypeHandler(type=Update, callback=cls.cancel.callback, )]  # See 1
            },
            fallbacks=[],
            conversation_timeout=DEFAULT_CH_TIMEOUT,
            allow_reentry=True,
            name='search'
        )
        if set_ch is True:
            cls.CH = result
        return result


class PublicPostCH:
    @staticmethod
    def create_entry_point():
        entry_point = CommandHandler(
            command=config.CREATE_PUBLIC_POST_S,
            callback=ptb_handlers.posts.CreatePublicPost.entry_point,
        )
        return entry_point

    @staticmethod
    def create_sample_handler():
        sample_handler = MessageHandler(
            filters=Filters.all,
            callback=ptb_handlers.posts.CreatePublicPost.sample_handler,
        )
        return sample_handler

    @staticmethod
    def create_confirm_handler():
        confirm_handler = MessageHandler(
            filters=Filters.text,
            callback=ptb_handlers.posts.CreatePublicPost.confirm_handler,
        )
        return confirm_handler

    entry_point = create_entry_point()
    cancel = create_cancel()
    sample_handler = create_sample_handler()
    confirm_handler = create_confirm_handler()
    CH: ConversationHandler = None

    @classmethod
    def create_ch(cls, set_ch: bool = True, ) -> ConversationHandler:
        ch = ConversationHandler(
            entry_points=[cls.entry_point],
            prefallbacks=[cls.cancel],
            states={
                0: [cls.sample_handler, ],
                1: [cls.confirm_handler, ],
            },
            fallbacks=[],
            conversation_timeout=DEFAULT_CH_TIMEOUT,
            allow_reentry=True,
            name='create_public_post'
        )
        if set_ch is True:
            cls.CH = ch
        return ch


class PersonalPostCH:
    @staticmethod
    def create_entry_point():
        entry_point = CommandHandler(
            command=config.CREATE_PERSONAL_POST_S,
            callback=ptb_handlers.posts.CreatePersonalPost.entry_point,
        )
        return entry_point

    @staticmethod
    def create_entry_point_handler():
        entry_point_handler = MessageHandler(
            filters=Filters.all,
            callback=ptb_handlers.posts.CreatePersonalPost.entry_point_handler,
        )
        return entry_point_handler

    @staticmethod
    def create_sample_handler():
        sample_handler = MessageHandler(
            filters=Filters.text,
            callback=ptb_handlers.posts.CreatePersonalPost.sample_handler,
        )
        return sample_handler

    @staticmethod
    def create_collections_handler():
        collections_handler = MessageHandler(
            filters=Filters.text,
            callback=ptb_handlers.posts.CreatePersonalPost.collections_handler,
        )
        return collections_handler

    @staticmethod
    def create_confirm_handler():
        confirm_handler = MessageHandler(
            filters=Filters.text,
            callback=ptb_handlers.posts.CreatePersonalPost.confirm_handler,
        )
        return confirm_handler

    entry_point = create_entry_point()
    cancel = create_cancel()
    entry_point_handler = create_entry_point_handler()
    sample_handler = create_sample_handler()
    collections_handler = create_collections_handler()
    confirm_handler = create_confirm_handler()
    CH: ConversationHandler = None

    @classmethod
    def create_ch(cls, set_ch: bool = True, ) -> ConversationHandler:
        ch = ConversationHandler(
            prefallbacks=[cls.cancel, ],
            entry_points=[cls.entry_point, ],
            states={
                0: [cls.entry_point_handler, ],
                1: [cls.sample_handler, ],
                2: [cls.collections_handler, ],
                3: [cls.confirm_handler, ],
            },
            fallbacks=[],
            conversation_timeout=DEFAULT_CH_TIMEOUT,
            allow_reentry=True,
            name='create_personal_post'
        )

        if set_ch is True:
            cls.CH = ch
        return ch


class SharePersonalPostsCh:

    @staticmethod
    def create_entry_point() -> CommandHandler:
        entry_point = CommandHandler(
            command=config.SHARE_PERSONAL_POSTS_S,
            callback=ptb_handlers.posts.SharePersonalPosts.entry_point,
        )
        return entry_point

    @staticmethod
    def create_recipient_handler() -> MessageHandler:
        recipient_handler = MessageHandler(
            filters=Filters.all,
            callback=ptb_handlers.posts.SharePersonalPosts.recipient_handler,
        )
        return recipient_handler

    cancel = create_cancel()
    entry_point = create_entry_point()
    recipient_handler = create_recipient_handler()
    CH = None

    @classmethod
    def create_ch(cls, set_ch: bool = True, ) -> ConversationHandler:
        ch = ConversationHandler(

            prefallbacks=[cls.cancel, ],
            entry_points=[cls.entry_point, ],
            states={0: [cls.recipient_handler, ], },
            fallbacks=[],
            conversation_timeout=DEFAULT_CH_TIMEOUT,
            allow_reentry=True,
            name='share_personal_posts'
        )
        if set_ch is True:
            cls.CH = ch
        return ch


class RequestPersonalPostsCH:
    @staticmethod
    def create_entry_point():
        entry_point = CommandHandler(
            command=config.REQUEST_PERSONAL_POSTS_S,
            callback=ptb_handlers.posts.RequestPersonalPosts.entry_point,
        )
        return entry_point

    @staticmethod
    def create_recipient_handler():
        recipient_handler = MessageHandler(
            filters=Filters.all,
            callback=ptb_handlers.posts.RequestPersonalPosts.recipient_handler,
        )
        return recipient_handler

    entry_point = create_entry_point()
    cancel = create_cancel()
    recipient_handler = create_recipient_handler()
    CH: ConversationHandler = None

    @classmethod
    def create_ch(cls, set_ch: bool = True, ) -> ConversationHandler:
        ch = ConversationHandler(
            entry_points=[cls.entry_point, ],
            prefallbacks=[cls.cancel, ],
            states={0: [cls.recipient_handler, ], },
            fallbacks=[],
            conversation_timeout=DEFAULT_CH_TIMEOUT,
            allow_reentry=True,
            name='request_personal_posts'
        )
        if set_ch is True:
            cls.CH = ch
        return ch


class GetStatisticWithCH:

    @staticmethod
    def create_entry_point() -> CommandHandler:
        entry_point = CommandHandler(
            command=config.GET_STATISTIC_WITH_S,
            callback=ptb_handlers.mix.GetStatisticWith.entry_point,
        )
        return entry_point

    @staticmethod
    def create_entry_point_handler() -> MessageHandler:
        entry_point_handler = MessageHandler(
            filters=Filters.text,
            callback=ptb_handlers.mix.GetStatisticWith.entry_point_handler,
        )
        return entry_point_handler

    cancel = create_cancel()
    entry_point = create_entry_point()
    entry_point_handler = create_entry_point_handler()
    CH: ConversationHandler = None

    @classmethod
    def create_ch(cls, set_ch: bool = True, ) -> ConversationHandler:
        result = ConversationHandler(
            prefallbacks=[cls.cancel, ],
            entry_points=[cls.entry_point, ],
            states={0: [cls.entry_point_handler], },
            fallbacks=[],
            conversation_timeout=DEFAULT_CH_TIMEOUT,
            allow_reentry=True,
            name='get_statistic_with'
        )
        if set_ch is True:
            cls.CH = result
        return result


def create_share_collections_ch() -> ConversationHandler:
    result = ConversationHandler(

        prefallbacks=[
            MessageHandler(
                filters=Filters.regex(constants.Regexp.CANCEL_R),
                callback=create_cancel().callback,
            ),
        ],

        entry_points=[
            CommandHandler(
                command=config.SHARE_COLLECTIONS_S,
                callback=ptb_handlers.collections.SharePersonalCollections.entry_point,
            )],

        states={
            0: [
                CallbackQueryHandler(
                    callback=ptb_handlers.collections.SharePersonalCollections.mark_to_share_cbk_handler,
                    pattern=config.MARK_COLLECTION_CBK_R,
                ),
                MessageHandler(
                    filters=Filters.text,
                    callback=ptb_handlers.collections.SharePersonalCollections.continue_handler,
                ),
            ],
            1: [MessageHandler(
                filters=Filters.all,
                callback=ptb_handlers.collections.SharePersonalCollections.recipient_handler,
            ),
            ],
        },
        fallbacks=[],
        conversation_timeout=DEFAULT_CH_TIMEOUT,
        allow_reentry=True,
        name='share_personal_collections'
    )
    return result


def create_autolog_handler() -> TypeHandler:
    result = TypeHandler(
        type=Update,
        callback=ptb_handlers.mix.auto_deb_logger,
    )
    return result


def create_log_update_handler() -> MessageHandler:
    result = MessageHandler(
        filters=Filters.attachment | Filters.text,
        callback=ptb_handlers.mix.log_update_handler,
    )
    return result


def create_log_call_stack_handler() -> TypeHandler:
    result = TypeHandler(
        type=Update,
        callback=ptb_handlers.mix.log_call_stack_handler,
    )
    return result


# # # CMD # # #

def create_help_cmd() -> CommandHandler:
    result = CommandHandler(
        command=config.ALL_BOT_COMMANDS_S,
        callback=ptb_handlers.mix.all_bot_commands_handler,
    )
    return result


def create_faq_cmd() -> CommandHandler:
    result = CommandHandler(
        command=config.FAQ_S,
        callback=ptb_handlers.mix.faq,
    )
    return result


def create_global_scenario_cmd() -> CommandHandler:
    result = CommandHandler(
        command=config.GLOBAL_SCENARIO_S,
        callback=ptb_handlers.start.GlobalScenario.entry_point,
    )
    return result


def create_get_public_post_cmd() -> CommandHandler:
    result = CommandHandler(
        command=config.GET_PUBLIC_POST_S,
        callback=ptb_handlers.posts.get_public_post,
    )
    return result


def create_get_my_personal_posts_cmd() -> CommandHandler:
    result = CommandHandler(
        command=config.GET_MY_PERSONAL_POSTS_S,
        callback=ptb_handlers.posts.get_my_personal_posts,
    )
    return result


def create_public_post_mass_sending_handler_cmd() -> CommandHandler:
    result = CommandHandler(
        command=config.SEND_S,
        callback=ptb_handlers.posts.public_post_mass_sending_handler,
        filters=Filters.user(ADMINS),
    )
    return result


def create_public_post_in_channel_handler_cmd() -> CommandHandler:
    result = CommandHandler(
        command=config.POST_S,
        callback=ptb_handlers.posts.public_post_in_channel_handler,
        filters=Filters.user(ADMINS),
    )
    return result


def create_get_pending_public_posts_handler_cmd() -> CommandHandler:
    result = CommandHandler(
        command=config.GET_PENDING_POSTS_S,
        callback=ptb_handlers.posts.get_pending_public_posts_handler,
        filters=Filters.user(ADMINS),
    )
    return result


def create_gen_bots_handler_cmd() -> CommandHandler:
    result = CommandHandler(
        command=config.GEN_BOTS_S,
        callback=ptb_handlers.mix.gen_bots_handler_cmd,
        filters=Filters.user(MAIN_ADMIN),
    )
    return result


def create_gen_me_handler_cmd() -> CommandHandler:
    result = CommandHandler(
        command=config.GEN_ME_S,
        callback=ptb_handlers.mix.gen_me_handler_cmd,
        filters=Filters.user(MAIN_ADMIN),
    )
    return result


def create_get_my_collections_handler_cmd() -> CommandHandler:
    result = CommandHandler(
        command=config.GET_MY_COLLECTIONS_S,
        callback=ptb_handlers.posts.get_my_collections_handler_cmd,
    )
    return result


def create_personal_example_handler_cmd() -> CommandHandler:
    result = CommandHandler(
        command=config.PERSONAL_EXAMPLE_S,
        callback=ptb_handlers.mix.personal_example,
    )
    return result


def create_start_handler_cmd() -> CommandHandler:
    result = CommandHandler(
        command=config.START_S,
        callback=ptb_handlers.start.entry_point,
    )
    return result


# # # CBK # # #

def create_accept_public_vote_cbk() -> CallbackQueryHandler:
    result = CallbackQueryHandler(
        callback=ptb_handlers.votes.public_vote_cbk_handler,
        pattern=config.PUBLIC_VOTE_CBK_R,
    )
    return result


def create_accept_channel_public_vote_cbk() -> CallbackQueryHandler:
    result = CallbackQueryHandler(
        callback=ptb_handlers.votes.channel_public_vote_cbk_handler,
        pattern=config.CHANNEL_PUBLIC_VOTE_CBK_R,  # Different vote behavior with regular public vote
    )
    return result


def create_accept_personal_vote_cbk() -> CallbackQueryHandler:
    result = CallbackQueryHandler(
        callback=ptb_handlers.votes.personal_vote_cbk_handler,
        pattern=config.PERSONAL_VOTE_CBK_R,
    )
    return result


def create_share_personal_post_cbk_handler() -> CallbackQueryHandler:  # Rename to posts
    result = CallbackQueryHandler(
        callback=ptb_handlers.posts.share_personal_posts_cbk_handler,
        pattern=config.ACCEPT_PERSONAL_POSTS_CBK_R,
    )
    return result


def create_accept_share_collections_cbk_handler() -> CallbackQueryHandler:
    result = CallbackQueryHandler(
        callback=ptb_handlers.collections.SharePersonalCollections.recipient_decision_cbk_handler,
        pattern=config.ACCEPT_COLLECTIONS_CBK_R,
    )
    return result


def create_show_collection_posts_personal_scenario_cbk_handler() -> CallbackQueryHandler:
    """
    Especially for personal scenario posts sharing cuz posts cbk handler for global and personal scenario are different
    """
    result = CallbackQueryHandler(
        callback=ptb_handlers.collections.SharePersonalCollections.show_collection_posts_to_recipient_cbk_handler,
        pattern=config.SHOW_COLLECTION_POSTS_CBK_R,
    )
    return result


def create_request_personal_post_cbk_handler() -> CallbackQueryHandler:
    result = CallbackQueryHandler(
        callback=ptb_handlers.posts.request_personal_post_cbk_handler,
        pattern=config.REQUEST_PERSONAL_POSTS_CBK_R,
    )
    return result


def create_update_public_post_status_cbk_handler() -> CallbackQueryHandler:
    result = CallbackQueryHandler(
        callback=ptb_handlers.posts.update_public_post_status_cbk,
        pattern=config.UPDATE_PUBLIC_POST_STATUS_CBK_R,
    )
    return result


def create_show_collection_posts_global_scenario_cbk_handler() -> CallbackQueryHandler:
    result = CallbackQueryHandler(
        callback=ptb_handlers.start.GlobalScenario.show_collection_posts_cbk_handler,
        # callback=app.tg.ptb.actions.show_collection_posts_cbk_handler,
        pattern=config.SHOW_COLLECTION_CBK_R,
    )
    return result


def create_empty_cbk_handler() -> CallbackQueryHandler:
    """Just do nothing on click"""
    result = CallbackQueryHandler(
        callback=ptb_handlers.mix.unclickable_cbk_handler,
        pattern=config.EMPTY_CBK_R,
    )
    return result


# CH
registration_ch = RegistrationCH.create_ch()
search_ch = SearchCH.create_ch()
public_post_ch = PublicPostCH.create_ch()
personal_post_ch = PersonalPostCH.create_ch()
share_personal_posts_ch = SharePersonalPostsCh.create_ch()
request_personal_posts_ch = RequestPersonalPostsCH.create_ch()
get_statistic_with_ch = GetStatisticWithCH.create_ch()
share_collections_ch = create_share_collections_ch()
personal_scenario_ch = PersonalScenarioCH.create_ch()
# PRE
autolog_handler = create_autolog_handler()
log_update_handler = create_log_update_handler()
log_call_stack_handler = create_log_call_stack_handler()
# CMD
help_handler_cmd = create_help_cmd()
faq_handler_cmd = create_faq_cmd()
global_scenario_cmd = create_global_scenario_cmd()
get_public_post_handler_cmd = create_get_public_post_cmd()
get_pending_public_posts_handler_cmd = create_get_pending_public_posts_handler_cmd()
get_my_personal_posts_handler_cmd = create_get_my_personal_posts_cmd()
public_post_mass_sending_handler_cmd = create_public_post_mass_sending_handler_cmd()
public_post_in_channel_handler_cmd = create_public_post_in_channel_handler_cmd()
personal_example_handler_cmd = create_personal_example_handler_cmd()
get_my_collections_handler_cmd = create_get_my_collections_handler_cmd()
start_handler_cmd = create_start_handler_cmd()
# CBK
accept_public_vote_handler_cbk = create_accept_public_vote_cbk()
accept_personal_vote_handler_cbk = create_accept_personal_vote_cbk()
share_personal_posts_handler_cbk = create_share_personal_post_cbk_handler()
request_personal_post_handler_cbk = create_request_personal_post_cbk_handler()
update_public_post_status_handler_cbk = create_update_public_post_status_cbk_handler()
show_collection_posts_global_scenario_cbk_handler = create_show_collection_posts_global_scenario_cbk_handler()
show_collection_posts_personal_scenario_cbk_handler = create_show_collection_posts_personal_scenario_cbk_handler()
accept_share_collections_handler_cbk = create_accept_share_collections_cbk_handler()
accept_channel_public_vote_cbk = create_accept_channel_public_vote_cbk()
empty_cbk_handler = create_empty_cbk_handler()
# GEN
gen_bots_handler_cmd = create_gen_bots_handler_cmd()
gen_me_handler_cmd = create_gen_me_handler_cmd()


def get_regular_handlers() -> list[DispatcherAddHandlerKwargs]:
    """Dict because need to specify additional args except the handler itself"""
    result = [
        # PRE
        {'handler': log_update_handler, 'group': -10},
        {'handler': autolog_handler, 'group': -9},
        # CMD
        {'handler': help_handler_cmd},
        {'handler': faq_handler_cmd},
        {'handler': global_scenario_cmd},
        {'handler': start_handler_cmd},
        {'handler': get_public_post_handler_cmd},
        {'handler': get_pending_public_posts_handler_cmd},
        {'handler': get_my_personal_posts_handler_cmd},
        {'handler': public_post_mass_sending_handler_cmd},
        {'handler': public_post_in_channel_handler_cmd},
        {'handler': get_my_collections_handler_cmd},
        {'handler': personal_example_handler_cmd},
        # CBK
        {'handler': accept_public_vote_handler_cbk},
        {'handler': accept_personal_vote_handler_cbk},
        {'handler': share_personal_posts_handler_cbk},
        {'handler': request_personal_post_handler_cbk},
        {'handler': update_public_post_status_handler_cbk},
        {'handler': show_collection_posts_global_scenario_cbk_handler},
        {'handler': show_collection_posts_personal_scenario_cbk_handler},
        {'handler': accept_share_collections_handler_cbk},
        {'handler': accept_channel_public_vote_cbk},
        {'handler': empty_cbk_handler},
        # GEN
        {'handler': gen_bots_handler_cmd},
        {'handler': gen_me_handler_cmd},
    ]
    # Mypy unable to recognize NotRequired type hint of  the DispatcherAddHandlerKwargs
    return result  # type: ignore[return-value]


def get_chs() -> list[DispatcherAddHandlerKwargs]:
    """Dict because need to specify additional args except the handler itself"""
    result = [
        {'handler': personal_scenario_ch},
        {'handler': registration_ch},
        {'handler': search_ch},
        {'handler': public_post_ch},
        {'handler': personal_post_ch},
        {'handler': share_personal_posts_ch},
        {'handler': request_personal_posts_ch},
        {'handler': get_statistic_with_ch},
        {'handler': share_collections_ch},
    ]
    # Mypy unable to recognize NotRequired type hint of  the DispatcherAddHandlerKwargs
    return result  # type: ignore[return-value]


def get_error_handlers() -> list[dict[str, Callable]]:
    return [
        # This handler also need to raise errors during tests,
        # otherwise the error will suppress by dispatcher and tests will be silently pass
        {'callback': ptb_handlers.mix.error_handler},
    ]


def set_handlers(
        dispatcher: Dispatcher,
        handlers: list[DispatcherAddHandlerKwargs],
        error_handlers: list[dict[str, Callable]],
) -> None:
    for handler in handlers:
        dispatcher.add_handler(**handler)
    for error_handler in error_handlers:
        dispatcher.add_error_handler(**error_handler)

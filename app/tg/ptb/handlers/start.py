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
from types import SimpleNamespace

from app.tg.ptb.classes.collections import Collection
from app.tg.ptb import services, config

if TYPE_CHECKING:
    # noinspection PyPackageRequirements
    from telegram import Update
    from custom_ptb.callback_context import CustomCallbackContext as CallbackContext


def entry_point(_: Update, context: CallbackContext, ):
    """Common entry point for both CHs"""
    context.user_data.view.cjm.start_scenario()
    return


class GlobalScenario:

    class CBK:
        cbk_map = {
            config.SHOW_COLLECTION_CBK_S: Collection.Keyboards.Show.extract_cbk_data,
        }

        @classmethod
        def extract(cls, cbk_data: str, ) -> int:
            lst_cbk_data = cbk_data.split()
            pattern = lst_cbk_data[0]
            extract_func = cls.cbk_map[pattern]
            result = extract_func(cbk_data=cbk_data, )
            return result

    @staticmethod
    def entry_point(_: Update, context: CallbackContext, ):
        default_collections = services.Collection.get_defaults(
            prefix=services.Collection.NamePrefix.PUBLIC.value,
        )
        services.Collection.Keyboards.set(
            collections=default_collections,
            keyboard=services.Collection.Mapper.Model.Keyboards.Show,
        )
        context.user_data.view.cjm.global_scenario_show_collections(collections=default_collections, )
        return 0

    @classmethod
    def show_collection_posts_cbk_handler(cls, update: Update, context: CallbackContext, ):
        try:
            collection_id = cls.CBK.extract(cbk_data=update.callback_query.data, )
            unprepared_posts = Collection.get_posts(
                collection_id=collection_id,
                connection=context.user_data.current_user.connection,
            )
            prepared_posts = services.Post.prepare_for_send(
                posts=unprepared_posts,
                clicker=context.user_data.current_user,  # In global scenario tg_user_id is equal (but not the obj)
                opposite=context.user_data.current_user,  # In global scenario tg_user_id is equal (but not the obj)
            )
            context.user_data.view.collections.show_collection_posts(posts=prepared_posts, )
            context.user_data.view.cjm.global_scenario_notify_ready_keyword()
        finally:
            update.callback_query.answer()


class PersonalScenario:

    class CBK:
        cbk_map = {
            config.SHOW_COLLECTION_POSTS_CBK_S: Collection.Keyboards.ShowPostsForRecipient.extract_cbk_data,
            config.MARK_SHOW_COLLECTION_CBK_S: Collection.Keyboards.MarkAndShow.extract_cbk_data,
        }

        @classmethod
        def extract(
                cls,
                cbk_data: str,
        ) -> tuple[Collection.Mapper.User, int]:
            lst_cbk_data = cbk_data.split()
            pattern = lst_cbk_data[0]
            extract_func = cls.cbk_map[pattern]
            result = extract_func(cbk_data=cbk_data, )
            return result

    @staticmethod
    def entry_point(_: Update, context: CallbackContext, ):
        default_collections = services.Collection.get_defaults(
            prefix=services.Collection.NamePrefix.PERSONAL.value,
        )
        collections = default_collections + context.user_data.current_user.get_collections()
        services.Collection.Keyboards.set(
            collections=collections,
            keyboard=services.Collection.Mapper.Model.Keyboards.MarkAndShow,
        )
        context.user_data.view.cjm.personal_scenario_show_collections(collections=collections, )
        context.user_data.view.notify_ready_keyword()
        return 0

    @classmethod
    def show_collection_posts_for_sender_cbk_handler(cls, update: Update, context: CallbackContext, ):
        """Show collection posts and mark it as shown (so the opponent wll get only shown collections)"""
        collection_id = cls.CBK.extract(cbk_data=update.callback_query.data, )
        context.user_data.tmp_data.collections_id_to_share.add(collection_id)
        unprepared_posts = Collection.get_posts(  # No matter tg or logic cls
            collection_id=collection_id,
            connection=context.user_data.current_user.connection,
        )
        prepared_posts = services.Post.prepare_for_send(
            posts=unprepared_posts,
            clicker=context.user_data.current_user,
            opposite=context.user_data.current_user,
        )
        context.user_data.view.collections.show_collection_posts(posts=prepared_posts, )
        context.user_data.view.notify_ready_keyword()
        update.callback_query.answer()

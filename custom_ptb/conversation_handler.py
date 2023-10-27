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

# noinspection PyPackageRequirements
from telegram.ext import (ConversationHandler,
                          CallbackQueryHandler,
                          ChosenInlineResultHandler,
                          Handler,
                          InlineQueryHandler, )
from threading import Lock
import logging
import warnings
# noinspection PyPackageRequirements
from telegram import Update
# noinspection PyPackageRequirements
from telegram.ext.utils.promise import Promise
from typing import Optional, Tuple
from custom_ptb.callback_context import CallbackContext

# pragma: no cover

CheckUpdateType = Optional[Tuple[Tuple[int, ...], Handler, object]]


class ConversationHandler(ConversationHandler):  # Override standard PTB class for "prefallbacks" list implementation

    def __init__(
            self,
            entry_points,
            prefallbacks,
            states,
            fallbacks,
            allow_reentry=False,
            per_chat=True,
            per_user=True,
            per_message=False,
            conversation_timeout=None,
            name=None,
            persistent=False,
            map_to_parent=None,
            run_async=False,
    ):
        super(ConversationHandler, self).__init__(entry_points,
                                                  states,
                                                  fallbacks,
                                                  allow_reentry=False,
                                                  per_chat=True,
                                                  per_user=True,
                                                  per_message=False,
                                                  conversation_timeout=None,
                                                  name=None,
                                                  persistent=False,
                                                  map_to_parent=None,
                                                  run_async=False, )
        self.run_async = run_async
        self._entry_points = entry_points
        self._prefallbacks = prefallbacks
        self._states = states
        self._fallbacks = fallbacks

        self._allow_reentry = allow_reentry
        self._per_user = per_user
        self._per_chat = per_chat
        self._per_message = per_message
        self._conversation_timeout = conversation_timeout
        self._name = name
        if persistent and not self.name:
            raise ValueError("Conversations can't be persistent when handler is unnamed.")
        self.persistent: bool = persistent
        self._persistence = None
        """:obj:`telegram.ext.BasePersistence`: The persistence used to store conversations.
        Set by dispatcher"""
        self._map_to_parent = map_to_parent

        self.timeout_jobs = {}
        self._timeout_jobs_lock = Lock()
        self._conversations = {}
        self._conversations_lock = Lock()

        self.logger = logging.getLogger(__name__)

        if not any((self.per_user, self.per_chat, self.per_message)):
            raise ValueError("'per_user', 'per_chat' and 'per_message' can't all be 'False'")

        if self.per_message and not self.per_chat:
            warnings.warn(
                "If 'per_message=True' is used, 'per_chat=True' should also be used, "
                "since message IDs are not globally unique."
            )

        all_handlers = []
        all_handlers.extend(prefallbacks)
        all_handlers.extend(entry_points)
        all_handlers.extend(fallbacks)

        for state_handlers in states.values():
            all_handlers.extend(state_handlers)

        if self.per_message:
            for handler in all_handlers:
                if not isinstance(handler, CallbackQueryHandler):
                    warnings.warn(
                        "If 'per_message=True', all entry points and state handlers"
                        " must be 'CallbackQueryHandler', since no other handlers "
                        "have a message context."
                    )
                    break
        else:
            for handler in all_handlers:
                if isinstance(handler, CallbackQueryHandler):
                    warnings.warn(
                        "If 'per_message=False', 'CallbackQueryHandler' will not be "
                        "tracked for every message."
                    )
                    break

        if self.per_chat:
            for handler in all_handlers:
                if isinstance(handler, (InlineQueryHandler, ChosenInlineResultHandler)):
                    warnings.warn(
                        "If 'per_chat=True', 'InlineQueryHandler' can not be used, "
                        "since inline queries have no chat context."
                    )
                    break

        if self.conversation_timeout:
            for handler in all_handlers:
                if isinstance(handler, self.__class__):
                    warnings.warn(
                        "Using `conversation_timeout` with nested conversations is currently not "
                        "supported. You can still try to use it, but it will likely behave "
                        "differently from what you expect."
                    )
                    break

        if self.run_async:
            for handler in all_handlers:
                handler.run_async = True

    """:obj:`int`: Used as a constant to handle state when a conversation is still waiting on the
    previous ``@run_sync`` decorated running handler to finish."""

    # pylint: disable=W0231

    @property
    def prefallbacks(self):
        """List[:class:`telegram.ext.Handler`]: A list of handlers that will be checked for handling
        before all the other handlers
        :obj:`False` on :attr:`check_update`.
        """
        return self._prefallbacks

    @prefallbacks.setter
    def prefallbacks(self, value: object):
        raise ValueError('You can not assign a new value to prefallbacks after initialization.')

    def check_update(self, update: object):  # pylint: disable=R0911
        """
        Determines whether an update should be handled by this conversationhandler, and if so in
        which state the conversation currently is.

        Args:
            update (:class:`telegram.Update` | :obj:`object`): Incoming update.

        Returns:
            :obj:`bool`

        """
        if not isinstance(update, Update):
            return None
        # Ignore messages in channels
        if update.channel_post or update.edited_channel_post:
            return None
        if self.per_chat and not update.effective_chat:
            return None
        if self.per_message and not update.callback_query:
            return None
        if update.callback_query and self.per_chat and not update.callback_query.message:
            return None

        key = self._get_key(update)
        with self._conversations_lock:
            state = self.conversations.get(key)

        # Resolve promises
        if isinstance(state, tuple) and len(state) == 2 and isinstance(state[1], Promise):
            self.logger.debug('waiting for promise...')

            # check if promise is finished or not
            if state[1].done.wait(0):
                res = self._resolve_promise(state)
                self._update_state(res, key)
                with self._conversations_lock:
                    state = self.conversations.get(key)

            # if not then handle WAITING state instead
            else:
                hdlrs = self.states.get(self.WAITING, [])
                for hdlr in hdlrs:
                    check = hdlr.check_update(update)
                    if check is not None and check is not False:
                        return key, hdlr, check
                return None

        self.logger.debug('selecting conversation %s with state %s', str(key), str(state))

        handler = None

        # Search entry points for a match
        if state is None or self.allow_reentry:
            for entry_point in self.entry_points:
                check = entry_point.check_update(update)
                if check is not None and check is not False:
                    handler = entry_point
                    return key, handler, check
            else:
                if state is None:
                    return None
        for prefallback in self.prefallbacks:  # My
            check = prefallback.check_update(update)  # My
            if check is not None and check is not False:  # My
                handler = prefallback  # My
                return key, handler, check  # My
        # Get the handler list for current state, if we didn't find one yet and we're still here
        if state is not None and not handler:
            handlers = self.states.get(state)
            for candidate in handlers or []:
                check = candidate.check_update(update)
                if check is not None and check is not False:
                    handler = candidate
                    return key, handler, check
            # Find a fallback handler if all other handlers fail
            else:
                for fallback in self.fallbacks:
                    check = fallback.check_update(update)
                    if check is not None and check is not False:
                        handler = fallback
                        return key, handler, check
        return None

    # def handle_update(  # type: ignore[override]
    #         self,
    #         update: Update,
    #         dispatcher: 'Dispatcher',
    #         check_result: CheckUpdateType,
    #         context: CallbackContext = None,
    # ) -> Optional[object]:
    #     # Original PTB action
    #     res = super().handle_update(update=update, dispatcher=dispatcher, check_result=check_result, context=context)
    #     if conversation_key not in self.conversations:  # If conversation was deleted by "END" state
    #         del context.conversation_data
    #     return res

    def go_back(self, context: CallbackContext = None, ):  # Not in use, kind of quickfix
        conversation_key, handler, _ = check_result  # type: ignore[assignment,misc]
        context.conversation_data.force_update({'current_conversation': self})
        context.conversation_data.force_update({'current_state': self.conversations.get(conversation_key)})
        if handler in self.states.get(self.conversations.get(conversation_key), self.entry_points):
            context.conversation_data['called_handlers'].append(handler)

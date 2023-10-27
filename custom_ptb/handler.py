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

from typing import TYPE_CHECKING, Callable, TypeVar, Union
# noinspection PyPackageRequirements
from telegram import Update
# noinspection PyPackageRequirements
from telegram.ext.utils.promise import Promise
# noinspection PyPackageRequirements
from telegram.utils.helpers import DefaultValue, DEFAULT_FALSE
# noinspection PyPackageRequirements
from telegram.ext.utils.types import CCT
# noinspection PyPackageRequirements
from telegram.ext import Handler
# noinspection PyPackageRequirements
from telegram.ext import CallbackContext


if TYPE_CHECKING:
    # noinspection PyPackageRequirements
    from telegram.ext import Dispatcher

RT = TypeVar('RT')
UT = TypeVar('UT')


class CustomHandler(Handler[Update, CCT]):

    def __init__(
            self,
            callback: Callable[[UT, CCT], RT],  # TODO Generic for **kwargs
            pass_update_queue: bool = False,
            pass_job_queue: bool = False,
            pass_user_data: bool = False,
            pass_chat_data: bool = False,
            run_async: Union[bool, DefaultValue] = DEFAULT_FALSE,
            *args,
            **kwargs,
    ):
        super().__init__(
            callback,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            pass_user_data=pass_user_data,
            pass_chat_data=pass_chat_data,
            run_async=run_async,
        )
        self.callback = callback
        self.pass_update_queue = pass_update_queue
        self.pass_job_queue = pass_job_queue
        self.pass_user_data = pass_user_data
        self.pass_chat_data = pass_chat_data
        self.run_async = run_async
        self.extra = kwargs.get('extra', [])
        self.args = args
        self.kwargs = kwargs

    def handle_update(
            self,
            update: UT,
            dispatcher: 'Dispatcher',
            check_result: object,
            context: CCT = None,
    ) -> Union[RT, Promise]:
        run_async = self.run_async
        if (
                self.run_async is DEFAULT_FALSE
                and dispatcher.bot.defaults
                and dispatcher.bot.defaults.run_async
        ):
            run_async = True

        if context:
            self.collect_additional_context(context, update, dispatcher, check_result)
            if run_async:
                return dispatcher.run_async(self.callback, update, context)
            return self.callback(update, context, **self._context_extractor(context=context, extra=self.extra))

        optional_args = self.collect_optional_args(dispatcher, update, check_result)
        if run_async:
            return dispatcher.run_async(
                self.callback, dispatcher.bot, update, update=update, **optional_args
            )
        return self.callback(dispatcher.bot, update, **optional_args)  # type: ignore

    def _context_extractor(self, context: CallbackContext, extra: dict) -> dict:
        extra_args = {}  # Handler definition
        callBACK_Signature = signature(self.callback)
        for arg in set(extra) & set(callBACK_Signature.parameters):
            try:
                extra_args[arg] = eval(extra[arg])
            except KeyError:
                if isinstance(callBACK_Signature.parameters[arg].default, _empty):
                    context.dispatcher.logger.warning(
                        msg=f"WARNING: You apparently will be get an error because expected"
                            f"variable {arg} of function {self.callback} don't found by the path {extra[arg]}")
                else:
                    context.dispatcher.logger.warning(
                        msg=f"WARNING: Variable '{arg}' don't found by the path '{extra[arg]}'.\n"
                            f"Please fix the variable path in the {self} handler")  # TODO show handler name
            except TypeError as e:  # Should be after KeyError
                raise TypeError(f'{e}\n'
                                f'{arg} argument with value {extra[arg]} of {self} handler must be string, '
                                f'got {type(extra[arg])}') from None  # From None to prevent error text duplication
        return extra_args

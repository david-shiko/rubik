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


class KnownException(Exception):
    pass


class IncorrectProfileValue(ValueError, KnownException):
    pass


class NoPhotos(KnownException, SystemError, ):
    pass


class NoVotes(KnownException, SystemError, ):
    pass


class NoCovotes(KnownException, SystemError, ):
    pass


class PostNotFound(KnownException, FileNotFoundError, ):
    pass


class IncorrectFinish(KnownException, ValueError, ):
    pass


class IncorrectSearchParameter(KnownException, ValueError, ):
    pass


class IncorrectVote(KnownException, ValueError, ):
    pass


class BadLocation(KnownException, ValueError, ):
    pass


class LocationServiceError(KnownException, SystemError, ):
    pass


class UserDeclinedRequest(KnownException, ValueError, ):
    pass


class DuplicateKeyError(KnownException, KeyError, ):
    pass


class ReqRequired(KnownException, ):
    pass


class UnexpectedException(Exception, ):
    pass


class UnknownVoteType(UnexpectedException, ValueError, ):
    def __init__(self, vote_type: Type):
        super(UnknownVoteType, self).__init__(f'Unknown vote type {vote_type}')


class UnknownPostType(UnexpectedException, ValueError, ):
    def __init__(self, post_type: Type | None = None, ):
        if post_type:
            message = f"Unknown {post_type}\n"
        else:
            message = ""
        super(UnknownPostType, self).__init__(message)


class DevException(Exception):
    pass


class ConnectionNotPassed(DevException):
    pass

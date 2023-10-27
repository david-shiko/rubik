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

from ._posts import public, personal, shared

PublicPostInterface = public.PostInterface
PersonalPostInterface = personal.PostInterface

PublicPost = public.Post
PersonalPost = personal.Post

PublicInterface = public.PostInterface
PersonalInterface = personal.PostInterface

Public = public.Post
Personal = personal.Post

PostProtocol = shared.PostProtocol
PostDC = shared.PostDC

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

from app.db.backup import create_db_backup_task
import app.db.manager
import app.tg.ptb.config
import app.tg.ptb.ptb_app

"""
To run the code use python -m
"""


def main():
    create_db_backup_task()
    bot = app.tg.ptb.ptb_app.create_ptb_bot()
    updater = app.tg.ptb.ptb_app.create_ptb_app(bot=bot)
    app.tg.ptb.ptb_app.configure_app(config=app.tg.ptb.config.Config(bot=bot, ))
    app.tg.ptb.ptb_app.start_ptb_bot(updater=updater, )  # Infinite blocking operation


if __name__ == '__main__':
    main()

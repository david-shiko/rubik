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

from subprocess import run as subprocess_run, CalledProcessError
from time import strftime as time_strftime
from os import environ as os_environ
import logging
import warnings
# noinspection PyProtectedMember
from pytz_deprecation_shim._exceptions import PytzUsageWarning

from app.postconfig import scheduler
from app.db import manager as db_manager
from app.config import PROJECT_ROOT_PATH


warnings.filterwarnings(
    action="ignore",
    category=PytzUsageWarning,
    module="apscheduler.util",
    message="The zone attribute is specific to pytz's interface;.*",
)
warnings.filterwarnings(
    action="ignore",
    category=PytzUsageWarning,
    module="apscheduler.triggers.interval",
    message="The normalize method is no longer necessary.*",
)


def perform_database_backup():
    backup_path = PROJECT_ROOT_PATH / 'db_backups' / f'{time_strftime("%Y-%m-%d_%H-%M-%S")}.sql'
    config = db_manager.Postgres.CONFIG
    # Maybe move to db manager?
    os_environ['PGPASSWORD'] = config.password  # Need to avoid bash pass prompt (he can't be accepted via cmd line)
    cmd_keys = f'--dbname={config.dbname} --user={config.user}  --host={config.host} --port={config.port}'
    backup_cmd = f"pg_dump {cmd_keys} > {backup_path}"
    logging.info("Starting database backup...")
    try:
        subprocess_run(backup_cmd, shell=True, check=True, )
        logging.info("Database backup completed successfully.")
    except CalledProcessError as e:
        logging.error(f"Database backup failed. {e.stderr}")
        raise e


def create_db_backup_task():
    scheduler.add_job(func=perform_database_backup, trigger='interval', days=1, )

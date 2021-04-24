#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Friendly Telegram (telegram userbot)
# Copyright (C) 2018-2019 GitHub/penn5

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# the logging things
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
LOGGER = logging.getLogger(__name__)

from telethon import errors


class MessageEditor():
    def __init__(self, message, command):
        self.message = message
        self.command = command
        self.stdout = ""
        self.stdin = ""
        self.stderr = ""
        self.rc = None
        self.redraws = 0
        self.process = None
        self.state = 0

    async def update_stdout(self, stdout):
        self.stdout = stdout
        await self.redraw()

    async def update_stderr(self, stderr):
        self.stderr = stderr
        await self.redraw()

    async def update_stdin(self, stdin):
        self.stdin = stdin
        await self.redraw()

    async def redraw(self, skip_wait=False):
        text = "Running command: {}".format(self.command) + "\n"
        if self.rc is not None:
            text += "process exited with code {}".format(str(self.rc))
        if len(self.stdout) > 0:
            text += "\n\n" + "STDOUT:" + "\n"
            text += "OUTPUT" + "\n" + self.stdout[max(len(self.stdout) - 2048, 0):] + "END OUTPUT"
        if len(self.stderr) > 0:
            text += "\n\n" + "STDERR:" + "\n"
            text += "\n" + self.stderr[max(len(self.stderr) - 1024, 0):] + "\n" + "END ERROR"
        if len(self.stdin) > 0:
            text += "\n\n" + "STDiN:" + "\n"
            text += "INPUT" + self.stdin[max(len(self.stdin) - 1024, 0):] + "END INPUT"
        try:
            await self.message.edit(text)
        except errors.rpcerrorlist.MessageNotModifiedError:
            pass
        except errors.rpcerrorlist.MessageTooLongError as e:
            LOGGER.error(e)
            LOGGER.error(text)
        # The message is never empty due to the template header

    async def cmd_ended(self, rc):
        self.rc = rc
        self.state = 4
        await self.redraw(True)

    def update_process(self, process):
        LOGGER.debug("got sproc obj %s", process)
        self.process = process

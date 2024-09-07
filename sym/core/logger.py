""" Logger of symbiot """

import enum
import inspect
import logging
import os
from logging import handlers, WARNING, StreamHandler

from pyrogram import Client

from sym.config import Config

os.makedirs("logs", exist_ok=True)


class LogLevels(enum.Enum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING


class Logger(Client):

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s - %(levelname)-8s - %(module)8s] - %(message)s",
        datefmt="%y.%m.%d %I:%M:%S %p",
        handlers={
            handlers.RotatingFileHandler(
                filename="logs/logs.txt",
                mode="a",
                maxBytes=4 * 1024 * 1024,
                backupCount=3,
                delay=False
            ),
            StreamHandler()
        }
    )
    logging.getLogger("pyrogram").setLevel(WARNING)
    logging.getLogger("httpx").setLevel(WARNING)
    logging.getLogger("aiohttp.access").setLevel(WARNING)

    @staticmethod
    def console_print(message: str):
        """ Print to console """
        stack = inspect.stack()[-2]
        line_num = stack.lineno
        file_name = stack.filename
        logging.log(logging.DEBUG, f"Logger in {file_name} at {line_num} ---\n{message}")

    @staticmethod
    def console_log(message: str, mode: LogLevels = LogLevels.INFO):
        """ Log to console """
        logging.log(mode.value, message)

    async def channel_log(self, message: str, dual: bool = False):
        """ Log to channel """
        if dual:
            self.console_log(message)
        await self.send_message(Config.LOG_CHANNEL_ID, message)

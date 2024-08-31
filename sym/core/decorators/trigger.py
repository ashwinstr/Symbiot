""" command decorator """
import os
import traceback
from typing import Callable, Any, Union

from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.filters import Filter
from pyrogram.handlers import MessageHandler, EditedMessageHandler
from pyrogram.types import Message

from sym.config import Config
from sym.core import types as _types


class Decorator(Client):
    """ custom decorator """

    def trigger(self, cmd: Union[str, Filter], group: int = 0):

        def inner(func: Callable[[Client, Message], Any]):

            async def wrapper(client: Client, message: Message):
                os.makedirs(Config.TEMP_DIR, exist_ok=True)
                os.makedirs(Config.DOWNLOAD_DIR, exist_ok=True)

                sym_message = _types.Message.parse(client, message)
                try:
                    await func(client, sym_message)
                except Exception as e:
                    await self.send_message(
                        Config.LOG_CHANNEL_ID,
                        "<b>#TRACEBACK</b>\n\n"
                        f"<b>Command:</b> {cmd if isinstance(cmd, str) else sym_message.cmd}\n"
                        f"<b>Module:</b> {func.__module__}\n"
                        f"<b>Function:</b> {func.__name__}\n"
                        f"<b>Error:</b> {e}\n\n"
                        f"<pre language=python>{traceback.format_exc()}</pre>",
                        parse_mode=ParseMode.HTML
                    )

            if isinstance(cmd, str):
                filtering = (filters.command(cmd, prefixes=Config.CMD_TRIGGER)) & filters.user(Config.OWNER_ID)
            elif isinstance(cmd, Filter):
                filtering = cmd
            else:
                filtering = None
            self.add_handler(
                MessageHandler(
                    wrapper, filters=filtering
                ),
                group=group
            )
            self.add_handler(
                EditedMessageHandler(
                    wrapper, filters=filtering
                ),
                group=group
            )

            return func
        return inner

""" command decorator """
import os
import traceback
from typing import Callable, Any, Union

from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.filters import Filter
from pyrogram.types import Message

import sym
from sym.config import Config
from sym.core import types as _types
from sym.core import handlers as _handlers
from sym.core.handlers import SymbiotHandler


class Decorator(Client):
    """ custom decorator """

    loaded_plugins = {}

    def trigger(self, cmd: Union[str, Filter], sudo: bool = False, group: int = 0):

        def inner(func: Callable[[Client, Message], Any]):

            async def wrapper(client: 'sym.Sym', message: Message):
                os.makedirs(Config.TEMP_DIR, exist_ok=True)
                os.makedirs(Config.DOWNLOAD_DIR, exist_ok=True)

                sym_message = _types.Message.parse(client, message)
                try:
                    await func(client, sym_message)
                except Exception as e:
                    await self.send_message(
                        Config.LOG_CHANNEL_ID,
                        "<b>#TRACEBACK</b>\n\n"
                        f"<b>Command:</b> <code>{cmd if isinstance(cmd, str) else sym_message.cmd}</code>\n"
                        f"<b>Module:</b> <code>{func.__module__}</code>\n"  # noqa
                        f"<b>Function:</b> <code>{func.__name__}</code>\n"
                        f"<b>Error:</b> <code>{e}</code>\n\n"
                        f"<pre language=python>{traceback.format_exc()}</pre>",
                        parse_mode=ParseMode.HTML
                    )

            if isinstance(cmd, str):
                filtering = SymbiotHandler.sym_filters(cmd, sudo)
            elif isinstance(cmd, Filter):
                filtering = cmd
            else:
                filtering = None

            handler = self.add_handler(SymbiotHandler(wrapper, filtering), group=group)
            _handlers.Load.Commands(cmd, func, handler, sudo)

            return func
        return inner

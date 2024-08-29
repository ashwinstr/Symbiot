""" command decorator """
from typing import Callable, Any

from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler, EditedMessageHandler
from pyrogram.types import Message

from sym.config import Config


class Decorator(Client):
    """ custom decorator """

    def trigger(self, cmd: str, group: int = 0):
        def inner(func: Callable[[Client, Message], Any]):
            async def wrapper(client: Client, message: Message):
                await func(self, message)

            self.add_handler(
                MessageHandler(
                    wrapper, filters=(filters.command(cmd, prefixes="<")) & filters.user(Config.OWNER_ID)
                ),
                group=group
            )
            self.add_handler(
                EditedMessageHandler(
                    wrapper, filters=(filters.command(cmd, prefixes="<")) & filters.user(Config.OWNER_ID)
                ),
                group=group
            )

            return func
        return inner

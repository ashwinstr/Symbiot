""" handlers for the bot """

from typing import Callable

from pyrogram.filters import Filter
from pyrogram.handlers import MessageHandler, EditedMessageHandler


class SymbiotHandler(MessageHandler, EditedMessageHandler):

    def __init__(self, func: Callable, filters: Filter = None):
        super().__init__(func, filters)

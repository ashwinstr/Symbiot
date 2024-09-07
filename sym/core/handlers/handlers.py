""" handlers for the bot """
import re
from typing import Callable

from pyrogram import filters
from pyrogram.filters import Filter
from pyrogram.handlers import MessageHandler, EditedMessageHandler

from sym.config import Config
from sym.core import types as _types


class SymbiotHandler(MessageHandler, EditedMessageHandler):

    def __init__(self, func: Callable, f: Filter = None):
        super().__init__(func, f)

    # @classmethod
    # def load(cls, func: Callable, f: Filter = None, group: int = 0) -> tuple[Handler, int]:
    #     Logger.console_log(f"Load plugin {func.__module__}.")
    #     return s.sym.add_handler(cls(func, f), group)
    #
    # @staticmethod
    # def unload(*args: tuple[Handler, int]):
    #     Logger.console_log("Unloaded plugin.")
    #     s.sym.remove_handler(*args)

    @staticmethod
    def _make_cmd_filters(m: "_types.Message", trigger: str, command: str) -> bool:
        if m and (m.text or m.caption):
            pattern = rf"^{trigger}{command}(?:\s([\S\s]+))?$"
            text = m.text or m.caption
            return bool(re.search(pattern, text))
        return False

    @staticmethod
    def sudo_filters(command: str) -> Filter:
        async def get_sudo_filters(_, __, m: "_types.Message") -> bool:
            user = m.from_user.id in Config.SUDO_USERS if m.from_user else False
            sudo_command = command in Config.SUDO_COMMANDS
            cmd_match = SymbiotHandler._make_cmd_filters(m, Config.SUDO_TRIGGER, command)
            return cmd_match and user and sudo_command
        return filters.create(get_sudo_filters, f"sudo_filter_{command}")

    @staticmethod
    def tsudo_filters(command: str) -> Filter:
        async def get_tsudo_filters(_, __, m: "_types.Message") -> bool:
            user = m.from_user.id in Config.TSUDO_USERS if m.from_user else False
            cmd_match = SymbiotHandler._make_cmd_filters(m, Config.SUDO_TRIGGER, command)
            return cmd_match and user
        return filters.create(get_tsudo_filters, f"tsudo_filters_{command}")

    @staticmethod
    def owner_filters(command: str) -> Filter:
        async def get_owner_filters(_, __, m: "_types.Message") -> bool:
            user = m.from_user.id == Config.OWNER_ID if m.from_user else False
            cmd_match = SymbiotHandler._make_cmd_filters(m, Config.CMD_TRIGGER, command)
            return cmd_match and user
        return filters.create(get_owner_filters, f"owner_filters_{command}")

    @staticmethod
    def sym_filters(cmd: str, sudo: bool) -> Filter:
        regex_ = r"[\\!@$^*()\-+\[\]{}|]"
        regex_found = re.search(regex_, cmd)
        if regex_found:
            filters_ = filters.regex(regex_)
        else:
            if sudo:
                filters_ = SymbiotHandler.owner_filters(cmd) | SymbiotHandler.sudo_filters(cmd) | SymbiotHandler.tsudo_filters(cmd)
            else:
                filters_ = SymbiotHandler.owner_filters(cmd) | SymbiotHandler.tsudo_filters(cmd)
        return filters_
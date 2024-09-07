""" configurations """

import os
from typing import Callable, List, Union, Any

from pyrogram import filters

from sym import core


class Config:

    API_HASH = os.environ.get("API_HASH")
    API_ID = int(os.environ.get("API_ID"))
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    CMD_TRIGGER = os.environ.get("CMD_TRIGGER", ".")
    DB_NAME = os.environ.get("DB_NAME", "Symbiot")
    DB_URL = os.environ.get("DB_URL")
    DEFAULT_PLUGINS: List[dict] = []
    DOWNLOAD_DIR = "downloads"
    INIT_TASKS = []
    LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID", 0))
    LOG_MODE = os.environ.get("LOG_MODE")
    OWNER_ID = int(os.environ.get("OWNER_ID", 0))
    SESSION_NAME = os.environ.get("SESSION_NAME", "Symbiot")
    STRING_SESSION = os.environ.get("STRING_SESSION")
    SUDO_COMMANDS = []
    SUDO_TRIGGER = os.environ.get("SUDO_TRIGGER", "!")
    SUDO_USERS = filters.user()
    TSUDO_USERS = filters.user()
    TEMP_DIR = "temp"

    @staticmethod
    async def save(config_name: str, value: Any) -> Any:
        """ add default plugins """
        config_name = config_name.upper()
        if not hasattr(Config, config_name):
            raise Config.InvalidConfigName(f"Config with name '{config_name}' not found.")
        collection = core.Collection("configs")
        await collection.add(
            {
                '_id': config_name,
                'data': value,
            }
        )
        setattr(Config, config_name, value)
        return value

    @staticmethod
    async def delete(config_name: str) -> bool:
        """ remove plugin """
        config_name = config_name.upper()
        if not hasattr(Config, config_name):
            raise Config.InvalidConfigName(f"Config with name '{config_name}' not found.")
        setattr(Config, config_name, None)
        collection = core.Collection("configs")
        found = collection.find_one({"_id": config_name})
        if found:
            await collection.remove({"_id": config_name})
            return True
        return False

    class InvalidConfigName(Exception):

        def __init__(self, message: str):
            super().__init__(message)
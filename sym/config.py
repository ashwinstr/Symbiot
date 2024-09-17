""" configurations """

import importlib
import os
from typing import List, Any

from pyrogram import filters

from sym import core


class Config:

    API_HASH = ""
    API_ID = ""
    BOT_TOKEN = ""
    CMD_TRIGGER = ""
    DB_NAME = ""
    DB_URL = os.environ.get("DB_URL")
    DEFAULT_PLUGINS: List[dict] = []
    DOWNLOAD_DIR = "downloads"
    INIT_TASKS = []
    LOG_CHANNEL_ID = 0
    LOG_MODE = os.environ.get("LOG_MODE")
    OWNER_ID = 0
    SESSION_NAME = ""
    STRING_SESSION = ""
    SUDO_COMMANDS = []
    SUDO_TRIGGER = ""
    SUDO_USERS = filters.user()
    TSUDO_USERS = filters.user()
    TEMP_DIR = "temp"
    WORK_DIR = os.environ.get("WORK_DIR")

    @staticmethod
    def get_external_configs():
        """ Load external configs """
        for_import = Config.WORK_DIR + ".config"
        module = importlib.import_module(for_import)
        configs = vars(getattr(module, "Config"))
        for var, val in configs.items():
            if not var.startswith("_"):
                setattr(Config, var, val)

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

Config.get_external_configs()
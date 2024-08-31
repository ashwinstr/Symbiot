""" configurations """

import os
from typing import Callable, List


class Config:

    API_HASH = os.environ.get("API_HASH")
    API_ID = int(os.environ.get("API_ID"))
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    CMD_TRIGGER = os.environ.get("CMD_TRIGGER", ".")
    DB_NAME = os.environ.get("DB_NAME", "Symbiot")
    DB_URL = os.environ.get("DB_URL")
    DEFAULT_PLUGINS: List[dict] = []
    DOWNLOAD_DIR = "downloads"
    LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID", 0))
    OWNER_ID = int(os.environ.get("OWNER_ID", 0))
    STRING_SESSION = os.environ.get("STRING_SESSION")
    SUDO_TRIGGER = os.environ.get("SUDO_TRIGGER", "!")
    TEMP_DIR = "temp"

    @staticmethod
    def add_plugin(cmd: str, func: Callable, module_path: str):
        """ add default plugins """
        Config.DEFAULT_PLUGINS.append(
            {
                'cmd': cmd,
                'func': func,
                'path': module_path
            }
        )

    @staticmethod
    def remove_plugin(cmd: str, func: Callable, module_path: str):
        """ remove plugin """
        dict_ = {
            'cmd': cmd,
            'func': func,
            'path': module_path
        }
        Config.DEFAULT_PLUGINS.remove(dict_)

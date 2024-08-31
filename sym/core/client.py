""" core to symbot """
import glob
import importlib
import os

from pyrogram import filters

import sym
from sym.config import Config
from sym.core import CustomClient


class Sym(CustomClient):

    def __init__(self):
        kwargs = {
            'name': os.environ.get("NAME"),
            'api_hash': os.environ.get("API_HASH"),
            'api_id': int(os.environ.get("API_ID", 0))
        }
        bot_token = os.environ.get("BOT_TOKEN")
        if bot_token:
            kwargs['bot_token'] = bot_token
        super().__init__(**kwargs)

    def _import_default_plugin(self):
        sep = os.path.sep
        default_plugins = glob.glob(os.path.join(sym.sym_dir, "**/[!^_]*.py"), recursive=True)
        for plugin in default_plugins:
            if plugin.endswith(".py"):
                module = plugin.split(f"site-packages{sep}")[1].replace(sep, ".")[:-3]
                importlib.import_module(module)
        for plugin in Config.DEFAULT_PLUGINS:
            owner_filters = filters.command(plugin['cmd'], prefixes=Config.CMD_TRIGGER) & filters.user(Config.OWNER_ID)
            self.trigger(owner_filters)(plugin['func'])

    @staticmethod
    def _import_plugins():
        module_path = os.environ.get("PLUGIN_DIR", ".")
        joined_path = f"{module_path}/**"
        modules = glob.glob(joined_path, recursive=True)
        for module in modules:
            path = module.replace("/", ".").replace("\\", ".")
            if path.endswith(".py"):
                module = path[:-3]
                importlib.import_module(module)


    async def start(
        self: "Sym"
    ):
        await super().start()
        await self.send_message(-1001636411318, "Bot started...")
        self._import_default_plugin()
        self._import_plugins()

    async def stop(
        self: "Sym",
        block: bool = True
    ):
        await super().stop(block=block)
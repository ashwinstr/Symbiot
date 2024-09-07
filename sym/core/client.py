""" core to symbot """
import asyncio
import glob
import importlib
import os

import sym
from sym.config import Config
from sym.core import CustomClient
from sym.core.handlers import SymbiotHandler
from sym.core.logger import LogLevels
from sym.core import handlers as _handlers


class Sym(CustomClient):

    def __init__(self):
        kwargs = {
            'name': Config.SESSION_NAME,
            'api_hash': Config.API_HASH,
            'api_id': Config.API_ID
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
                imported = importlib.import_module(module)
                if hasattr(imported, "_init"):
                    Config.INIT_TASKS.append(getattr(Config, "_init"))
        for plugin in Config.DEFAULT_PLUGINS:
            _filters = SymbiotHandler.owner_filters(plugin['cmd']) | SymbiotHandler.tsudo_filters(plugin['cmd'])
            self.trigger(_filters)(plugin['func'])

    @staticmethod
    def _import_plugins():
        module_path = os.environ.get("PLUGIN_DIR", ".")
        joined_path = f"{module_path}/**"
        modules = glob.glob(joined_path, recursive=True)
        for module in modules:
            path = module.replace("/", ".").replace("\\", ".")
            if path.endswith(".py"):
                module = path[:-3]
                imported = importlib.import_module(module)
                if hasattr(imported, "_init"):
                    Config.INIT_TASKS.append(getattr(Config, "_init"))

    def _initiate_listener(self):
        self.listener = self.Interact.add_listener(self)  # listener added


    async def start(
        self: "Sym"
    ):
        await super().start()
        print(
            "\n--------------------------------------- Session started ---------------------------------------"
        )
        self.console_log("Symbiot booted.")

        self._import_default_plugin()
        self.console_log("Inbuilt plugins loaded.")

        self._import_plugins()
        self.console_log("All plugins loaded.")

        self._initiate_listener()

        await asyncio.gather(*Config.INIT_TASKS)
        self.console_log("All initial functions executed.")

    async def stop(
        self: "Sym",
        block: bool = True
    ):
        self.Interact.remove_listener(self, self.listener)  # listener removed
        self.console_log(
            "Stopping the bot."
            "\n---------------------------------------- Session ended ----------------------------------------\n",
            LogLevels.WARNING
        )
        await super().stop(block=block)

    async def restart(
        self: "Sym",
        block: bool = True
    ):
        ...

    def reload_plugins(self):
        plugin_dict = self.CMDS
        plugins = plugin_dict.keys()
        for plugin in plugins:
            command: 'sym.Sym.Commands' = plugin_dict[plugin]
            self.remove_handler(*command.handler)
            module = importlib.import_module(command.module)
            importlib.reload(module)
""" core to symbot """
import asyncio
import glob
import importlib
import os

import sym
from sym.config import Config
from sym.core import CustomClient, helpers as _helpers
from sym.core.logger import LogLevels


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

    @staticmethod
    async def _import_default_plugins(reload: bool = False, reload_core: bool = False):
        if reload_core:
            if Config.OWNER_ID == 1013414037 and os.path.exists("config.env"):
                mod = "../Symbiot"
            else:
                mod = "sym@git+https://github.com/ashwinstr/Symbiot@master"
            await _helpers.run_shell_cmd(f"pip install -U {mod}")
        sep = os.path.sep
        default_plugins = glob.glob(os.path.join(sym.sym_dir, "**/[!^_]*.py"), recursive=True)
        for plugin in default_plugins:
            if plugin.endswith(".py"):
                module = plugin.split(f"site-packages{sep}")[1].replace(sep, ".")[:-3]
                imported = importlib.import_module(module)
                if reload:
                    importlib.reload(imported)
                if hasattr(imported, "_init"):
                    Config.INIT_TASKS.append(getattr(imported, "_init"))

    @staticmethod
    def _import_plugins(reload: bool = False):
        module_path = os.environ.get("PLUGIN_DIR", ".")
        joined_path = f"{module_path}/**"
        modules = glob.glob(joined_path, recursive=True)
        for module in modules:
            path = module.replace("/", ".").replace("\\", ".")
            if path.endswith(".py"):
                module = path[:-3]
                imported = importlib.import_module(module)
                if reload:
                    importlib.reload(imported)
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

        await self._import_default_plugins()
        self.console_log("Inbuilt plugins loaded.")

        self._import_plugins()
        self.console_log("All plugins loaded.")

        self._initiate_listener()

        await asyncio.gather(*Config.INIT_TASKS)
        Config.INIT_TASKS = []
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
        await super().restart(block)

    async def reload_bot(self, include_core: bool = False):
        plugin_dict = self.CMDS
        plugins = plugin_dict.keys()
        for plugin in plugins:
            command: 'sym.Sym.Commands' = plugin_dict[plugin]
            self.remove_handler(*command.handler)
            self.Interact.remove_listener(self, self.listener)
            importlib.invalidate_caches()
        await self._import_default_plugins(True, include_core)
        self._import_plugins(True)
        await asyncio.gather(*Config.INIT_TASKS)
        Config.INIT_TASKS = []
        self.console_log("Plugins reload ended successfully.")
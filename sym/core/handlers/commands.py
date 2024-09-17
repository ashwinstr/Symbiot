""" Command manager """

from typing import Callable, Dict

from pyrogram import Client


class Load(Client):

    CMDS: Dict[str, 'Commands'] = {}

    class Commands:

        def __init__(self, cmd: str, func: Callable, handler: tuple, sudo: bool = False):
            self.doc = func.__doc__ or "Not documented."
            self.func = func
            self.handler = handler
            self.name = cmd
            self.module = func.__module__  # noqa
            self.sudo = sudo
            self.store()

        def store(self):
            Load.CMDS[self.name] = self

        @staticmethod
        def get_cmd(cmd_name: str, null_return: bool = False) -> 'Load.Commands|None':
            dict_ = Load.CMDS.get(cmd_name, None)
            if not dict_ and not null_return:
                raise Load.Commands.CommandNotFound(cmd_name)
            return dict_


        class CommandNotFound(Exception):
            
            def __init__(self, cmd_name: str):
                super().__init__(f"Command named '{cmd_name}' not found.")
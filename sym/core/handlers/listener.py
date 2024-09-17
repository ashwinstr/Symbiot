""" Interaction handler """
import asyncio
from collections import defaultdict
from typing import Dict

from pyrogram import Client, filters as f
from pyrogram.filters import Filter

import sym
from sym.core import handlers
from sym.core import types as _types


class Listener(Client):
    """ Conversation class """

    interaction_dict: Dict[int, dict] = {}

    class Interact:

        def __init__(self, chat_id: int, filters: Filter = None):
            self.filters = filters
            self.chat_id = chat_id
            self.future = asyncio.get_event_loop().create_future()
            self.response: '_types.Message|None' = None

        @staticmethod
        def add_listener(client: 'sym.Sym') -> tuple:
            filter_ = f.create(lambda _, __, m: m.chat.id in Listener.interaction_dict.keys())
            return client.add_handler(handlers.SymbiotHandler(DefaultListener.handler(), filter_), group=-1)

        @staticmethod
        def remove_listener(client: 'sym.Sym', handler: tuple):
            client.remove_handler(*handler)

        def refresh_future(self):
            if self.future.done():
                self.future = asyncio.get_event_loop().create_future()
                Listener.interaction_dict[self.chat_id] = {'future': self.future}

        async def read(self, filters: Filter = None, timeout: int = 15) -> '_types.Message':
            self.refresh_future()
            Listener.interaction_dict[self.chat_id]['filters'] = filters if filters else self.filters
            try:
                response = await asyncio.wait_for(self.future, timeout)
                self.response = response
            except (asyncio.TimeoutError, TimeoutError):
                raise self.TimeoutError(f"Timeout error after waiting for {timeout}s.")
            return response

        async def write_message(self, text: str) -> '_types.Message':
            send_ = await sym.sym.send_message(self.chat_id, text)
            return send_

        async def __aenter__(self):
            if self.chat_id in Listener.interaction_dict.keys():
                raise self.DuplicateInteraction(self.chat_id)
            Listener.interaction_dict[self.chat_id] = {'future': self.future}
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            Listener.interaction_dict.pop(self.chat_id, None)
            
            
        class TimeoutError(Exception):
            
            def __init__(self, message: str):
                super().__init__(message)

        class DuplicateInteraction(Exception):

            def __init__(self, chat_id: int):
                super().__init__(f"Interaction instance with {chat_id} already exists.")

class DefaultListener:

    @staticmethod
    def handler():
        async def listener_callback(c, m):
            message = _types.Message.parse(c, m)
            dict_ = Listener.interaction_dict.get(message.chat.id)
            if not dict_:
                return
            if not dict_['filters'] or not await dict_['filters'](c, message):
                return
            if not dict_['future'].done():
                dict_['future'].set_result(message)

        return listener_callback
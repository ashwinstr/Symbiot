""" Monkeypatch to Pyrogram's Message """

import os.path
import re
from typing import List, Union

from pyrogram.enums import ParseMode
from pyrogram.errors import MessageAuthorRequired, MessageIdInvalid
from pyrogram.filters import Filter
from pyrogram.types import Message as PyroMessage

import sym
from sym.config import Config


class Message(PyroMessage):
    
    def __init__(self, client: 'sym.Sym', message, **kwargs):
        self._client = client
        super().__init__(client=client, **message, **kwargs)

    @classmethod
    def parse(cls, client: 'sym.Sym', message: PyroMessage, **kwargs):
        vars_ = vars(message)
        if "_client" in vars_.keys():
            del vars_['_client']
        return cls(client, vars_, **kwargs)

    @property
    def cmd(self) -> str:
        return self.text.split()[0].strip(Config.CMD_TRIGGER)

    @property
    def flags(self) -> List[Union[str, dict]]:
        list_ = []
        text = self.text.splitlines()[0]
        found = re.findall(r"-\w", text)
        for flag in found:
            list_.append(flag)
        return list_

    @property
    def filter_text(self) -> str:
        flags = self.flags
        input_ = self.input_str
        for one in flags:
            input_ = input_.replace(one, "")
        return input_.strip()

    @property
    def input_str(self) -> str:
        text = self.text
        return_str = text.split(maxsplit=1)
        if len(return_str) != 2:
            return ""
        return return_str[1]

    @property
    def replied(self) -> 'Message':
        return self.reply_to_message

    @property
    def unique_id(self) -> str:
        return f"{self.chat.id}.{self.id}"


    async def edit(
            self,
            text: str,
            parse_mode: ParseMode = ParseMode.DEFAULT,
            disable_preview: bool = False,
            **kwargs
    ) -> 'Message':
        """ overridden edit method """
        try:
            message: 'Message' = await super().edit(text, parse_mode, disable_web_page_preview=disable_preview, **kwargs)
        except (MessageAuthorRequired, MessageIdInvalid):
            message = await self._client.send_message(
                self.chat.id,
                text,
                parse_mode,
                reply_to_message_id=self.reply_to_message.id if self.reply_to_message else None,
                disable_web_page_preview=disable_preview
            )
        self.id = message.id
        return self.parse(message._client,message)

    async def err(
            self,
            text: str,
            parse_mode: ParseMode = ParseMode.DEFAULT,
            disable_preview: bool = False,
            **kwargs
    ) -> 'Message':
        """ error message editing """
        return await self.edit(f"**Error:** {text}", parse_mode=parse_mode, disable_preview=disable_preview, **kwargs)

    async def send_as_file(
            self,
            text: str,
            file_name: str = "file.txt",
            caption: str = "",
            reply_id: int = None,
            **kwargs
    ) -> 'Message':
        """ convert text to file and send as document """
        file_path = os.path.join(Config.TEMP_DIR, file_name)
        with open(file_path, "w+", encoding="utf-8") as file_:
            file_.write(text)
        if not reply_id:
            reply_id = self.reply_to_message_id if self.reply_to_message else None
        message = await self._client.send_document(self.chat.id, file_path, file_name=file_name, reply_to_message_id=reply_id, caption=caption, **kwargs)
        return self.parse(self._client, message)

    async def read_response(self, filters: Filter = None, timeout: int = 15, ) -> 'Message':
        async with self._client.Interact(self.chat.id, filters=filters) as _int:
            response = await _int.read(timeout=timeout)
        return response

    def interact(self, filters: Filter = None) -> 'sym.sym.Interact':
        return self._client.Interact(self.chat.id, filters)
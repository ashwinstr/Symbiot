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
    def cmd(self) -> str|None:
        match_ = re.search(rf"^{Config.CMD_TRIGGER}(\w+)(?:\s\S.*)?", self.text)
        if match_:
            return self.text.split()[0].lstrip(Config.CMD_TRIGGER)
        return None

    @property
    def flags(self) -> List[Union[str, dict]]:
        list_ = []
        text = self.text.splitlines()[0]
        found_dict: List[tuple] = re.findall(r"(-[a-z]+)(\d+)\s", text)
        found_string: List[re.Match] = re.findall(r"(-[a-z]+)\s", text)
        for dict_flag in found_dict:
            list_.append({dict_flag[0]: dict_flag[1]})
        for str_flag in found_string:
            list_.append(str_flag)
        return list_

    @property
    def filter_text(self) -> str:
        flags = self.flags
        input_ = self.input_str
        for one in flags:
            flag = ""
            if isinstance(one, dict):
                for key in one:
                    flag = f"{key}{one[key]}"
            else:
                flag = one
            input_ = input_.replace(flag, "")
        return input_.strip()

    @property
    def input_str(self) -> str:
        text = self.text
        return_str = text.split(maxsplit=1)
        if len(return_str) != 2:
            return ""
        return return_str[1].strip()

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
            reply_to_id: int = None,
            **kwargs
    ) -> 'Message':
        """ overridden edit method """
        if not reply_to_id:
            reply_to_id = self.reply_to_message_id
        try:
            message: 'Message' = await super().edit(text, parse_mode, disable_web_page_preview=disable_preview, **kwargs)
        except (MessageAuthorRequired, MessageIdInvalid):
            message = await self._client.send_message(
                self.chat.id,
                text,
                parse_mode,
                reply_to_message_id=reply_to_id,
                disable_web_page_preview=disable_preview
            )
        self.id = message.id
        return self.parse(message._client,message)

    async def edit_mono(self, text: str, disable_preview: bool = False, **kwargs) -> 'Message':
        """ Edit message with mono text markdown """
        text = f"```text\n{text}```"
        return await self.edit(text, parse_mode=ParseMode.MARKDOWN, disable_preview=disable_preview, **kwargs)

    async def edit_or_send_file(
            self,
            text: str,
            file_name: str = "file.txt",
            caption: str = "",
            parse_mode: ParseMode = ParseMode.DEFAULT,
            disable_preview: bool = False,
            reply_to_id: int = None
    ) -> 'Message':
        """ Safe edit text """
        if len(text) <= 4096:
            return await self.edit(
                text,
                parse_mode=parse_mode,
                disable_preview=disable_preview,
                reply_to_id=reply_to_id
            )
        return await self.send_as_file(text, file_name, caption, reply_to_id)

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
            reply_id = self.reply_to_message_id
        message = await self._client.send_document(self.chat.id, file_path, file_name=file_name, reply_to_message_id=reply_id, caption=caption, **kwargs)
        return self.parse(self._client, message)

    async def read_response(self, filters: Filter = None, timeout: int = 15, ) -> 'Message':
        async with self._client.Interact(self.chat.id, filters=filters) as _int:
            response = await _int.read(timeout=timeout)
        return response

    def interact(self, filters: Filter = None) -> 'sym.sym.Interact':
        return self._client.Interact(self.chat.id, filters)

    async def interact_once(self, text: str, filters: Filter = None, timeout: int = 15) -> 'Message':
        """ Interact wrapper for single response """
        async with self.interact(filters=filters) as _i:
            await _i.write_message(text=text)
            reply_ = await _i.read(filters=filters, timeout=timeout)
        return reply_
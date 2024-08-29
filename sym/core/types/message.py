""" Monkeypatch to pyrogram's Message """

from pyrogram.types import Message as PyroMessage


class Message(PyroMessage):
    
    def __init__(self):
        super().__init__(id=self.id)

    @property
    def input_str(self) -> str:
        text = self.text
        return_str = text.split(" ", 1)[1]
        return return_str

    @property
    def replied(self) -> 'Message':
        return self.reply_to_message

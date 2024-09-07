""" logs plugin for the core """

import aiofiles

from sym import sym, Sym, Message


@sym.trigger("logs", sudo=True)
async def send_logs(s: Sym, message: Message):
    print("Dynamically loaded.")
    limit = message.input_str
    async with aiofiles.open("logs/logs.txt", "r") as file_:
        text = await file_.read()
    if limit and limit.isdigit():
        lines = text.splitlines()
        start_line = len(lines) - int(limit)
        text = "\n".join(lines[start_line:])
    text = f"<pre language=python>{text}</pre>"
    if len(text) <= 4080:
        await message.edit(text)
    else:
        await message.reply_document("logs/logs.txt")
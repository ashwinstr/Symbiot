""" backbone of the bot """
import asyncio
import sys
import traceback
from io import StringIO

from pyrogram.enums import ParseMode

from sym import Sym, Message
from sym.config import Config


async def _executor(sym: Sym, message: Message):
    input_ = message.input_str
    if not input_:
        return await message.err("`Input not found...`")
    await message.edit("`Evaluating...`")
    sys.stdout = codeOut = StringIO()
    sys.stderr = codeErr = StringIO()
    formatted_code = "\n    ".join(input_.splitlines())
    try:
        exec(f"async def _exec(bot, message):\n    {formatted_code}")
        func_out = await asyncio.Task(
            locals()["_exec"](sym, message), name=message.unique_id
        )
    except asyncio.CancelledError:
        return await message.edit("`Cancelled...`")
    except BaseException:
        func_out = traceback.format_exc()
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    output = codeErr.getvalue().strip() or codeOut.getvalue().strip()

    if func_out is not None:
        output = f"{output}\n\n{func_out}".strip()
    output = f"```python\n{input_}```\n\n>> ```\n{output}```"
    if len(output) < 4096:
        await message.edit(output, parse_mode=ParseMode.MARKDOWN, disable_preview=True)
    else:
        await message.edit("`Output too big.`")

Config.add_plugin(
    cmd="eval",
    func=_executor,
    module_path=_executor.__module__
)
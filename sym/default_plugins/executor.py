""" Backbone plugin of the bot """

import asyncio
import sys
import traceback
from io import StringIO

from pyrogram.enums import ParseMode

from sym import sym as s, Sym, Message
from sym.config import Config


async def _executor(sym: Sym, message: Message):
    input_ = message.filter_text
    flags = message.flags
    if not input_:
        return await message.err("`Input not found...`")
    if "-p" in flags and hasattr(Config, "LAST_EVAL_MESSAGE"):
        msg = Config.LAST_EVAL_MESSAGE
        start_message = "`Executing eval on last message...`"
    else:
        msg = message
        start_message = "`Executing new eval...`"
    await msg.edit(start_message)
    sys.stdout = codeOut = StringIO()
    sys.stderr = codeErr = StringIO()
    formatted_code = "\n    ".join(input_.splitlines())
    try:
        exec(f"async def _exec(sym, message):\n    {formatted_code}")
        func_out = await asyncio.Task(
            locals()["_exec"](sym, msg), name=msg.unique_id
        )
    except asyncio.CancelledError:
        delattr(Config, "LAST_EVAL_MESSAGE")
        return await msg.edit("`Cancelled...`")
    except BaseException:
        func_out = traceback.format_exc()
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    output = codeErr.getvalue().strip() or codeOut.getvalue().strip()

    if func_out is not None:
        output = f"{output}\n\n{func_out}".strip()
        if output == "":
            output = str(True)
    output = f"```python\n{input_}```\n\n>> ```\n{output}```"
    if len(output) < 4096:
        await msg.edit(output, parse_mode=ParseMode.MARKDOWN, disable_preview=True)
    else:
        await asyncio.gather(
            msg.send_as_file(output, "eval.txt", input_),
            msg.delete()
        )
    setattr(Config, "LAST_EVAL_MESSAGE", msg)

# Config.add_plugin(
#     cmd="py",
#     func=_executor,
#     module_path=_executor.__module__
# )

Config.DEFAULT_PLUGINS.append(
    {
        'cmd': "py",
        'func': _executor,
        'path': _executor.__module__
    }
)
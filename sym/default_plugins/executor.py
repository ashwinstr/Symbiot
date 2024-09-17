""" Backbone plugin of the bot """

import asyncio
import sys
import traceback
from io import StringIO

from pyrogram.enums import ParseMode

from sym import Sym, Message, sym
from sym.config import Config
from sym.core.helpers import shell, AsyncShell
from . import f
from ..core.helpers.shell import InteractiveShell


@sym.trigger('py')
async def _executor(s: Sym, message: Message):
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
    except BaseException:  # noqa
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


@sym.trigger('sh')
async def _terminal(_, message: Message):
    """ Terminal """
    cmd = message.input_str
    await message.edit_mono("Executing shell...")
    try:
        stdout = await asyncio.create_task(
            shell.run_shell_cmd(cmd), name=message.unique_id
        )
    except asyncio.CancelledError:
        return await message.edit_mono("Cancelled.")
    output = f"```shell\n~${cmd}```\n```shell\n{stdout}```"
    return await message.edit_or_send_file(output, file_name="shell.txt")


# Shell with Live Output
async def _async_shell(s: Sym, message: Message):
    cmd = message.input_str
    await message.edit_mono("Getting live output...")
    sub_process = await shell.AsyncShell.run_cmd(cmd)
    sleep_for = 1
    output = ""
    try:
        async for stdout in sub_process.get_output():
            if output != stdout:
                await message.edit(
                    text=f"```shell\n{stdout}```",
                    disable_preview=True,
                    parse_mode=ParseMode.MARKDOWN,
                )
                output = stdout
            if sleep_for >= 6:
                sleep_for = 2
            await asyncio.create_task(asyncio.sleep(sleep_for), name=message.unique_id)
            sleep_for += 2
        await message.edit_or_send_file(
            text=f"<pre language=shell>~${cmd}\n\n{sub_process.full_std}</pre>",
            file_name="shell.txt",
            disable_preview=True,
        )
    except asyncio.exceptions.CancelledError:
        sub_process.cancel()
        await message.edit_mono(f"Cancelled...")
    except BaseException as e:
        sub_process.cancel()
        await s.channel_log(name=__name__, message=str(e))


async def _interactive_shell_func(message: Message, cmd: str, terminal: 'shell.AsyncShell'):
    """ Interactive shell """
    output = ""
    sleep_for = 1
    format_ = (
        "~${cmd}\n\n{output}"
    )
    try:
        async for stdout in terminal.get_output():
            if output != stdout:
                await message.edit(
                    text=f"```shell\n{stdout}```",
                    disable_preview=True,
                    parse_mode=ParseMode.MARKDOWN,
                )
                output = stdout
            if sleep_for >= 6:
                sleep_for = 2
            await asyncio.create_task(asyncio.sleep(sleep_for), name=message.unique_id)
            sleep_for += 2
        full_output = format_.format(cmd=cmd, output=terminal.full_std)
        length = len(full_output)
        if length >= 4096:
            diff = abs(length - 4096)
            to_length = len(terminal.full_std) - diff
            full_output = format_.format(cmd=cmd, output=terminal.full_std[-to_length:])
        await message.reply(full_output)
    except asyncio.exceptions.CancelledError:
        terminal.cancel()
        await message.edit_mono(f"Cancelled...")
    except BaseException as e:
        terminal.cancel()
        await sym.channel_log(name=__name__, message=str(e))


async def _interactive_shell_1(_, message: Message):
    """ Interactive shell """
    cmd = message.input_str
    terminal = await AsyncShell.run_cmd(cmd)
    await _interactive_shell_func(message, cmd, terminal)
    while not terminal.cancelled:
        try:
            next_ = await message.interact_once(
                "Next command: ",
                f.command("nextsh", prefixes="<") & f.user(message.from_user.id if message.from_user else Config.OWNER_ID),
                timeout=30
            )
        except (TimeoutError, asyncio.TimeoutError, asyncio.CancelledError, sym.Interact.TimeoutError):
            await message.reply("`Terminal timeout...`")
            return terminal.cancel()
        next_cmd = next_.input_str
        test = await terminal.next_cmd(next_cmd)
        await message.reply(f"{cmd}\n```{test.full_std}```")


async def _interactive_shell(_, message: Message):
    """ Test """
    cmd = message.input_str
    terminal = await InteractiveShell.start_command(cmd)

    async def callback():
        if terminal.output:
            await message.reply(f"```bash\n{terminal.output}```")
        else:
            await message.reply("Output is empty...\nWaiting for next command.")
        terminal.output = ""
        try:
            next_ = await message.interact_once(
                "Send next command...",
                f.user(message.from_user.id) & f.command(['nextsh', 'cancel'], prefixes="<"),
                timeout=30
            )
            if next_.cmd == "cancel":
                terminal.cancel()
                return
            await terminal.next_command(next_.input_str)

        except sym.Interact.TimeoutError:
            terminal.cancel()
            print("Timeout.")
        except BaseException as e:
            await sym.channel_log(__name__, str(e))

    while not terminal.cancelled:
        await terminal.process.wait()
        await callback()


# Config.DEFAULT_PLUGINS.extend([
#     {
#         'cmd': 'py',
#         'func': _executor,
#         'path': _executor.__module__
#     },
#     {
#         'cmd': 'sh',
#         'func': _terminal,
#         'path': _terminal.__module__
#     },
#     {
#         'cmd': 'ash',
#         'func': _async_shell,
#         'path': _async_shell.__module__
#     },
#     {
#         'cmd': 'ish',
#         'func': _interactive_shell,
#         'path': _interactive_shell.__module__
#     }
# ])
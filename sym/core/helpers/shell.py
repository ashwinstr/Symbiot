""" Respectfully kanged from ub-core """ # noqa

import asyncio
from typing import AsyncGenerator, Any


async def run_shell_cmd(
    cmd: str, timeout: int = 300, ret_val: Any | None = None
) -> str:
    """ Runs a shell command and returns Output """
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )
    try:
        async with asyncio.timeout(timeout):
            stdout, _ = await proc.communicate()
            return stdout.decode("utf-8")
    except (asyncio.CancelledError, TimeoutError):
        proc.kill()
        if ret_val is not None:
            return ret_val
        raise

class AsyncShell:

    def __init__(self, process: asyncio.subprocess.Process):
        """Not to Be Invoked Directly.\n
        Use AsyncShell.run_cmd"""
        self.command = ""
        self.name = ""
        self.process = process
        self.full_std: str = ""
        self.last_line: str = ""
        self.is_done: bool = False
        self._task: asyncio.Task | None = None

    @property
    def cancelled(self) -> bool:
        if self._task.cancelled():
            return True
        return False

    async def read_output(self) -> None:
        """Read StdOut/StdErr and append to full_std and last_line"""
        async for line in self.process.stdout:
            decoded_line = line.decode("utf-8")
            self.full_std += decoded_line
            self.last_line = decoded_line
        self.is_done = True
        await self.process.wait()

    async def get_output(self) -> AsyncGenerator:
        while not self.is_done:
            yield self.full_std if len(self.full_std) < 4000 else self.last_line
            await asyncio.sleep(0)

    def cancel(self) -> bool:
        if not self.is_done:
            self.process.kill()
            self._task.cancel()
            return True
        return False

    @classmethod
    async def run_cmd(cls, cmd: str, name: str = "AsyncShell") -> "AsyncShell":
        """Setup Object, Start Fetching output and return the process Object."""
        sub_process = cls(
            process=await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
        )
        sub_process.command = cmd
        sub_process.name = name
        sub_process._task = asyncio.create_task(sub_process.read_output(), name=name)
        await asyncio.sleep(0.5)
        return sub_process

    async def next_cmd(self, next_cmd: str) -> 'AsyncShell':
        self.command += f" && {next_cmd}"
        process = await asyncio.create_subprocess_shell(
            self.command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )
        self.process = process
        self._task = asyncio.create_task(self.read_output(), name=self.name)
        await asyncio.sleep(0.5)
        return self


class InteractiveShell:

    def __init__(self, process: asyncio.subprocess.Process = None):  # noqa
        self._task: asyncio.Task|None = None
        self.command = ""
        self.is_done = False
        self.last_command = ""
        self.last_output = ""
        self.name = ""
        self.output = ""
        self.process = process

    @classmethod
    async def start_command(cls, command: str, name: str = "InteractiveShell"):
        process = cls(
            await asyncio.create_subprocess_shell(
                cmd=command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
        )
        process.command = command
        process.name = name
        process._task = asyncio.create_task(process.read_output(), name=name)
        return process

    @property
    def cancelled(self) -> bool:
        return self._task.cancelled()

    async def next_command(self, command: str):
        self.last_command = command
        self.command += f" && {command}"
        self.process = await asyncio.create_subprocess_shell(
            self.command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )
        self._task = asyncio.create_task(self.read_output(), name=self.name)

    async def read_output(self) -> None:
        output = ""
        while not self.is_done:
            line = (await self.process.stdout.readline()).decode("utf-8")
            if not line or line.strip() == "Interactive shell done.":
                break
            output += line
        output = output.replace(self.last_output, "")
        self.last_output = output
        self.output = output

    def cancel(self) -> bool:
        self.command = ""
        self.last_command = ""
        if not self.is_done:
            self.process.kill()
            self._task.cancel()
            return True
        return False
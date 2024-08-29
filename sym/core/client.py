""" core to symbot """

from pyrogram import Client, idle


class Sym(Client):

    def __init__(self):
        super().__init__(name="Symbot")

    async def start(
        self: "Sym"
    ):
        await super().start()
        print("Started bot...")
        await idle()

    async def stop(
        self: "Sym",
        block: bool = True
    ):
        await super().stop(block=block)
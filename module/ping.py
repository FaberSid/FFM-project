from discord.ext import commands as c
import time


class Ping(c.Cog):
    def __init__(self, bot):
        self.bot = bot

    @c.command()
    async def ping(self, ctx):
        before = time.monotonic()
        msg = await ctx.send("Pong!")
        ping = (time.monotonic() - before) * 1000
        await msg.edit(content=f"Pong!  `{int(ping)}ms`")


def setup(bot):
    bot.add_cog(Ping(bot))

from discord.ext import commands as c
import discord
import time
import psutil


class Cog(c.Cog):
    def __init__(self, bot):
        self.bot = bot

    @c.command()
    async def ping(self, ctx):
        before = time.monotonic()
        msg = await ctx.send("Pong!")
        ping = (time.monotonic() - before) * 1000
        embed = discord.Embed()
        embed.add_field(name="ping", value=f"{int(ping)}ms", inline=False)
        embed.add_field(name="latency", value=f"{int(self.bot.latency*1000)}ms", inline=False)
        embed.add_field(name="メモリ使用率", value=f"{psutil.virtual_memory().percent}％", inline=False)
        embed.add_field(name="CPU使用率", value=f"{psutil.cpu_percent(interval=1)}％", inline=False)
        await msg.edit(content=None, embed=embed)


def setup(bot):
    bot.add_cog(Cog(bot))

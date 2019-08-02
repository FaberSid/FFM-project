from discord.ext import commands as c
from discord import Forbidden
from module import db


def table(_, message):
    prefix_s = db.prefix(message.guild).get()
    if prefix_s:
        return prefix_s
    else:
        return "]]"


class Prefix(c.Cog):
    def __init__(self, bot):
        self.bot = bot

    @c.Cog.listener()
    async def on_message(self, msg):
        if msg.content.startswith(f"<@{self.bot.user.id}>"):
            await msg.channel.send(f"`{table(None, msg)}help`でヘルプが見れます")

    @c.command()
    async def prefix(self, ctx, *, prefix_str):
        prefix_s = db.prefix(ctx.guild).get()
        if not prefix_s:
            db.prefix(ctx.guild).register(prefix_str)
        try:
            await ctx.guild.get_member(self.bot.user.id).edit(nick=f"[{prefix_str}]{self.bot.user.name}")
        except Forbidden:
            pass


def setup(bot):
    bot.add_cog(Prefix(bot))

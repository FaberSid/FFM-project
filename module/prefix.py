from discord.ext import commands as c
from discord import Forbidden
from module import db


def table(bot, message):
    prefix_s = db.prefix(message.guild).get()
    default = [f"<@{bot.user.id}> ", f"<@!{bot.user.id}> "]
    return [prefix_s] + default


class Cog(c.Cog):
    def __init__(self, bot):
        self.bot = bot

    @c.command()
    async def prefix(self, ctx, *, prefix_str=None):
        if prefix_str is None:
            await ctx.send("プレフィックスが指定されていません")
        else:
            try:
                await ctx.guild.get_member(self.bot.user.id).edit(nick=f"[{prefix_str}]{self.bot.user.name}")
                db.prefix(ctx.guild).register(prefix_str)
            except Forbidden:
                pass


def setup(bot):
    bot.add_cog(Cog(bot))

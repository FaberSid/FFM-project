from discord.ext import commands as c
from discord import Forbidden, HTTPException
from module import db


def table(bot, message):
    prefix_s = db.prefix(message.guild).get()
    default = [f"<@{bot.user.id}> ", f"<@!{bot.user.id}> "]
    return [prefix_s] + default


class Cog(c.Cog):
    def __init__(self, bot):
        self.bot = bot

    @c.command()
    @c.has_permissions(administrator=True)
    async def prefix(self, ctx, *, prefix_str=None):
        if prefix_str is None:
            await ctx.send(f"プレフィックスが指定されていません\n今のプレフィックスは{db.prefix(ctx.guild).get()}です。")
        else:
            if len(prefix_str) > 5:
                await ctx.send("プレフィックスは５文字に抑えてくださいな")
            else:
                db.prefix(ctx.guild).register(prefix_str)


def setup(bot):
    bot.add_cog(Cog(bot))

from discord.ext import commands as c
from module import db
from module import battle


class Reset(c.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @c.command(aliases=['re', 'rs'], pass_context=True, description='戦いをやり直す')
    async def reset(self, ctx):
        """戦いをやり直す"""
        if db.channel.is_battle(ctx.message.channel.id):
            await battle.reset_battle(ctx, ctx.message.channel.id, False)
        else:
            await ctx.send("このチャンネルでは戦いは行われていないようだ。")


def setup(bot):
    bot.add_cog(Reset(bot))

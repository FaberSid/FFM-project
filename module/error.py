from discord.ext import commands as c
from discord import Embed
import traceback
import getpass


class CmdNotFoundError(c.Cog):
    def __init__(self, bot):
        self.bot = bot

    @c.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, c.errors.CommandNotFound):
            return
        a = traceback.format_exception(type(error), error, error.__traceback__)
        text = ""
        ch = self.bot.get_channel(597363081928245248)
        for x in a:
            x = x.replace(f"\\{getpass.getuser()}\\", "\\*\\")
            if len(text + x) < 2000-9:
                text += x
            else:
                await ch.send(f"```py\n{text}```")
                text = x
        await ch.send(f"```py\n{text}```")
        embed = Embed(description="発言元：[移動](https://discordapp.com/channels/"
                                  f"{ctx.guild.id}/{ctx.channel.id}/{ctx.message.id})")
        await ch.send("<@&599220739815505941>修正よろしくね！", embed=embed)


def setup(bot):
    bot.add_cog(CmdNotFoundError(bot))

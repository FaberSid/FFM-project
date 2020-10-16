import asyncio
import re

from discord import Embed, Guild, NotFound, PartialInviteGuild
from discord.ext import commands as c


class Cog(c.Cog):
    def __init__(self, bot):
        self.bot=bot


    @c.Cog.listener()
    async def on_message(self, messages):
        if messages.channel.id == 421954703509946368:
            tao = await self.bot.fetch_emoji(623907445416263680)
            url = re.findall("discord.gg/([a-zA-Z1-9]+)", messages.content)
            url += re.findall("invite/([a-zA-Z1-9]+)", messages.content)
            for i in url:
                try:
                    invite = await self.bot.fetch_invite(i)
                    if isinstance(invite.guild, Guild):
                        await messages.add_reaction(tao)
                        return
                except NotFound:
                    pass
        elif messages.channel.id == 609008926767185950:
            ffm = await self.bot.fetch_emoji(691027670900670576)
            url = re.findall("discord.gg/([a-zA-Z1-9]+)", messages.content)
            url += re.findall("invite/([a-zA-Z1-9]+)", messages.content)
            for i in url:
                try:
                    invite = await self.bot.fetch_invite(i)
                    if isinstance(invite.guild, Guild):
                        await messages.add_reaction(ffm)
                        return
                except NotFound:
                    pass

    async def on_message_edit(self, _, after):
        if self.bot.is_ready():
            await self.on_message(after)

    @c.command()
    async def invite(self, ctx):
        await ctx.send(embed=Embed(description="[FFM公式鯖(Discord)](https://discord.gg/Pvu2h2E)\n"
                                               "[FFMボットの招待(Discord)](https://discordapp.com/oauth2/authorize?client_id=574476342163406858&scope=bot&permissions=67493056)\n"
                                               "[supported by TAO](https://discord.gg/ETNbhqD)"))

def setup(bot):
    bot.add_cog(Cog(bot))

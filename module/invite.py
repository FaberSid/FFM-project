import asyncio
import re

from discord import Guild, NotFound, PartialInviteGuild
from discord.ext import commands as c


class Invite(c.Cog):
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
            url = re.findall("discord.gg/([a-zA-Z1-9]+)", messages.content)
            url += re.findall("invite/([a-zA-Z1-9]+)", messages.content)
            for i in url:
                try:
                    invite = await self.bot.fetch_invite(i)
                    if isinstance(invite.guild, Guild):
                        await messages.add_reaction("🇫")
                        return
                except NotFound:
                    pass

    async def on_message_edit(self, _, after):
        if self.bot.is_ready():
            await self.on_message(after)


def setup(bot):
    bot.add_cog(Invite(bot))

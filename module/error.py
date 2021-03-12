import getpass
import hashlib
import math
import traceback

import aiohttp
from discord import (AsyncWebhookAdapter, Embed, File, RawReactionActionEvent,
                     Webhook)
from discord.ext import commands as c

from module import item, status


async def _webhook(all_error, url, ctx):
    for i in range(len(all_error)):
        while len("".join(all_error[i:i+2])) < 1800 and len("".join(all_error[i+1:])) != 0:
            all_error[i:i+2] = ["".join(all_error[i:i+2])]
    async with aiohttp.ClientSession() as session:
        w = Webhook.from_url(url, adapter=AsyncWebhookAdapter(session))
        for i in range(0, len(all_error), 3):
            await w.send(file=File("variables.txt"), content=f"```py\n! ERROR:{ctx.author}    ID:{ctx.author.id}\n! 鯖名:{ctx.guild}    チャンネル名:{ctx.channel}\nBOTか否か:{ctx.author.bot}```", embeds=[Embed(title="TAO内部のError情報:", description=f"```py\n{y.replace('`', '')}```").set_footer(text=f"{i + x + 1}/{len(all_error)}") for x, y in enumerate(all_error[i:i + 3])])


class Cog(c.Cog):
    def __init__(self, bot):
        self.bot = bot

    @c.Cog.listener()
    async def on_command_error(self, ctx, error):
        if not __debug__:
            if any([isinstance(error, i) for i in [c.CommandInvokeError, c.CommandNotFound, c.BadArgument, c.UnexpectedQuoteError, c.ExpectedClosingQuoteError, c.InvalidEndOfQuotedStringError]]):
                traceback.print_exception(type(error), error, error.__traceback__)
                print(dir(error))
                return
            elif isinstance(error, c.DisabledCommand):
                await ctx.send(embed=Embed(description="実行したコマンドは開発中か諸事情により開発者が無効化しています"))
                return
        l_error = traceback.format_exception(
            type(error), error, error.__traceback__)
        l_error = [x.replace(f"\\{getpass.getuser()}\\", "\\*\\")
                   for x in l_error if "site-packages" not in x]
        webhook = await self.bot.fetch_webhook(712268338189041730)
        cnt = None
        hash_error = hashlib.sha512(
            bytes("".join(l_error), 'shift-jis')).hexdigest()

        async for message in webhook.channel.history(limit=None):
            if message.embeds:
                if message.embeds[0].footer.text == hash_error and message.embeds[0].author.name:
                    if cnt is None:
                        cnt = 1 + int(message.embeds[0].author.name[:-8])
                    await message.delete()
        cnt = cnt or 1

        def is_limit(embeds, description=""):
            """FIELD	LIMIT
            title	     256 characters
            description	2048 characters
            fields  Up to 25 field objects
            field.name	 256 characters
            field.value	1024 characters
            footer.text	2048 characters
            author.name  256 characters
            Additionally, the characters in all title, description, field.name, field.value, footer.text, and author.name fields must not exceed 6000"""
            if len(embeds) == 0:
                embeds += [Embed(description=description)]
                return embeds, ""
            elif 9*sum([bool(e.description) for e in embeds])+sum(map(len, sum([[e.title, e.description, e.footer.text, e.author.name, *sum([[i.name, i.value] for i in e.fields], []), description] for e in embeds], []))) > 6000:
                return embeds, description
            elif len(embeds[-1].description)+len(description) <= 2048-9:
                if embeds[-1].description:
                    embeds[-1].description += description
                else:
                    embeds[-1].description = description
                return embeds, ""
            elif len(embeds) < 10:
                embeds += [Embed(description=description)]
                return embeds, ""
            else:
                return embeds, description

        top = Embed(title="{}: {}".format(type(error).__name__, error)[:256]).set_author(
            name=f"{cnt}回目のエラーです").set_footer(text=hash_error)
        l_embeds = [[top.copy()]]
        description = ""
        l_error += ["\n#END Traceback```\n**発生場所**\nGuild:{}(ID:{})\nchannel:{}(ID:{})\nuser:{}(ID:{})\nLink:[ここ]({})\n```escape".format(
            ctx.guild.name, ctx.guild.id, ctx.channel.name, ctx.channel.id, ctx.author.name, ctx.author.id, ctx.message.jump_url)]
        while l_error:
            if not description:
                description = l_error.pop(0)
            l_embeds[-1], description = is_limit(l_embeds[-1], description)
            if description:
                l_embeds += [[top.copy()]]
        for i in l_embeds:
            for j in i:
                j.description = "```py\n"+j.description+"```"
        for i, embeds in enumerate(l_embeds):
            await webhook.send(None if i else "<@&599220739815505941>修正よろしくね！", embeds=embeds, wait=True)
        if cnt == 1:
            item.obtain_an_item(ctx.author.id, -8)
            exp = math.ceil(status.get_player_level(ctx.author.id) / 7)
            first_err_msg = "\n\nあ、またバグが見つかったんだ。\nしかも今までにないエラーか\n<@{}>は{}の経験値と{}を得た。\n{}".format(
                ctx.author.id, exp, item.items.get("-8", {"name": "unknown"})["name"], status.experiment(ctx.author.id, exp))
        else:
            first_err_msg = ""
        await ctx.send(embed=Embed(title="エラーが発生しました", description="発生したエラーは開発者が調査中です"+first_err_msg).set_footer(text="hash: "+hash_error))


def setup(bot):
    bot.add_cog(Cog(bot))

import os
import random

import psycopg2
from discord import Embed, RawReactionActionEvent
from discord.ext import commands as c

from module import battle, db


class Cog(c.Cog):
    def __init__(self, bot):
        self.bot = bot

    @c.command(description='ランキングが知れます')
    @c.cooldown(10, 2, c.BucketType.user)
    async def rank(self, ctx):
        msg = await ctx.send(embed=Embed(description="1\u20e3 プレイヤーランキング\n"
                                                     "2\u20e3 チャンネルランキング(global)\n"
                                                     "3\u20e3 チャンネルランキング(local)\n"
                                                     "~~4\u20e3 倒した敵の数ランキング~~\n").set_footer(text="cmd.rank"))
        self.bot.on_cmd -= {ctx.author.id}
        for i in range(4):
            if str(msg.embeds[0].footer.text) != "cmd.rank":
                return
            await msg.add_reaction("%s\u20e3" % (i+1))

    @c.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        msg = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        if msg.author == self.bot.user and payload.user_id != self.bot.user.id and msg.embeds:
            button = ["\u23ee", "\u25c0", "\u23f9", "\u25b6",
                      "\u23ed", "\U0001f201", "\U0001f504"]

            async def refresh_rank1(msg, offset=None, limit=10):
                rank, ranking, _cache = db.player.experience.ranking(
                    payload.user_id, offset, limit)
                user = self.bot.get_user(payload.user_id)
                if rank:
                    embed = Embed(title="{}位　{}(Lv.{})".format(
                        rank[0], user, int(rank[2]**0.5)))
                else:
                    embed = Embed(title="ランキング外　{}".format(user))
                embed.description = "\n".join(["{}位　{}(Lv.{})".format(
                    i[0], self.bot.get_user(i[1]), int(i[2]**0.5)) for i in ranking])
                embed.set_author(name="プレイヤーランキング")
                embed.set_footer(text="cmd.rank.player\u200b{}\u200b{}".format(
                    *map(lambda x: hex(x)[2:], _cache)))
                await msg.edit(embed=embed)

            async def refresh_rank2(msg, is_local=False, offset=None, limit=10):
                rank, ranking, _cache = db.channel.ranking(
                    msg, is_local, offset, limit)
                name = self.bot.get_channel(payload.channel_id).name
                if rank:
                    embed = Embed(title="{}位　{}(Lv.{})".format(
                        rank[0], name, rank[3]))
                else:
                    embed = Embed(title="ランキング外　{}".format(name))
                embed.description = "\n".join(["{}位　<#{}>(Lv.{})".format(
                    i[0], i[1], i[3]) for i in ranking])
                if is_local:
                    embed.set_author(name="プレイヤーランキング(サーバー内)")
                    embed.set_footer(text="cmd.rank.channel.local\u200b{}\u200b{}".format(
                        *map(lambda x: hex(x)[2:], _cache)))
                else:
                    embed.set_author(name="プレイヤーランキング(全体)")
                    embed.set_footer(text="cmd.rank.channel.global\u200b{}\u200b{}".format(
                        *map(lambda x: hex(x)[2:], _cache)))
                await msg.edit(embed=embed)

            offset = None
            limit = 10
            if str(payload.emoji) == "\u23ee":  # first
                offset = 0
            elif str(payload.emoji) == "\u25c0":  # left
                offset, limit = map(lambda x: int(x, 16), str(
                    msg.embeds[0].footer.text).split("\u200b")[1:])
                offset = offset-limit
                if offset < 0:
                    return
            elif str(payload.emoji) == "\u23f9":  # stop
                await msg.clear_reactions()
                return
            elif str(payload.emoji) == "\u25b6":  # right
                offset, limit = map(lambda x: int(x, 16), str(
                    msg.embeds[0].footer.text).split("\u200b")[1:])
                offset = offset+limit
                if len(db.player.experience()) < offset:
                    return
            elif str(payload.emoji) == "\u23ed":  # last
                limit = int(
                    str(msg.embeds[0].footer.text).split("\u200b")[2], 16)
                offset = len(db.player.experience())//limit*limit
            elif str(payload.emoji) == "\U0001f201":  # here
                pass
            elif str(payload.emoji) == "\U0001f504":  # reload
                offset, limit = map(lambda x: int(x, 16), str(
                    msg.embeds[0].footer.text).split("\u200b")[1:])
            if str(msg.embeds[0].footer.text).startswith("cmd.rank.player"):
                await refresh_rank1(msg, offset, limit)
            elif str(msg.embeds[0].footer.text).startswith("cmd.rank.channel.local"):
                await refresh_rank2(msg, True, offset, limit)
            elif str(msg.embeds[0].footer.text).startswith("cmd.rank.channel.global"):
                await refresh_rank2(msg, False, offset, limit)
            if str(msg.embeds[0].footer.text) == "cmd.rank":
                if str(payload.emoji) == "1\u20e3":
                    await refresh_rank1(msg, offset)
                    await msg.clear_reactions()
                    for emoji in ["\u23ee", "\u25c0", "\u23f9", "\u25b6", "\u23ed", "\U0001f201", "\U0001f504"]:
                        await msg.add_reaction(emoji)
                elif str(payload.emoji) == "2\u20e3":
                    await refresh_rank2(msg, False, offset)
                    await msg.clear_reactions()
                    for emoji in ["\u23ee", "\u25c0", "\u23f9", "\u25b6", "\u23ed", "\U0001f504"]:
                        await msg.add_reaction(emoji)
                elif str(payload.emoji) == "3\u20e3":
                    await refresh_rank2(msg, True, offset)
                    await msg.clear_reactions()
                    for emoji in ["\u23ee", "\u25c0", "\u23f9", "\u25b6", "\u23ed", "\U0001f504"]:
                        await msg.add_reaction(emoji)


def setup(bot):
    bot.add_cog(Cog(bot))

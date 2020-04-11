import os
import random

import psycopg2
import requests
from discord import Embed
from discord.ext import commands as c

from module import battle, db


class Cog(c.Cog):
    def __init__(self, bot):
        self.bot = bot

    @c.command(description='ランキングが知れます')
    @c.cooldown(10, 2, c.BucketType.user)
    async def rank(self, ctx):
        msg = await ctx.send(embed=Embed(description="1\u20e3 プレイヤーランキング\n"
                                                     "~~2\u20e3 チャンネルランキング~~\n"
                                                     "~~3\u20e3 倒した敵の数ランキング~~\n").set_footer(text="cmd.rank"))
        for i in range(3):
            if str(msg.embeds[0].footer.text) != "cmd.rank":
                return
            await msg.add_reaction("%s\u20e3" % (i+1))

    @c.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        msg = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        if msg.author == self.bot.user and payload.user_id != self.bot.user.id and msg.embeds:
            if str(msg.embeds[0].footer.text).startswith("cmd.rank.player"):
                if str(payload.emoji) == "\u23ee":  # first
                    rank, ranking, _cache = db.player.experience.ranking(
                        payload.user_id,0)
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
                elif str(payload.emoji) == "\u25c0":  # left
                    offset,limit = map(lambda x:int(x,16),str(msg.embeds[0].footer.text).split("\u200b")[1:])
                    offset = offset-limit
                    if offset < 0:
                        return
                    rank, ranking, _cache = db.player.experience.ranking(
                        payload.user_id,offset)
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
                elif str(payload.emoji) == "\u23f9":  # stop
                    await msg.clear_reactions()
                elif str(payload.emoji) == "\u25b6":  # right
                    offset,limit = map(lambda x:int(x,16),str(msg.embeds[0].footer.text).split("\u200b")[1:])
                    offset = offset+limit
                    if len(db.player.experience()) < offset:
                        return
                    rank, ranking, _cache = db.player.experience.ranking(
                        payload.user_id,offset)
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
                elif str(payload.emoji) == "\u23ed":  # last
                    limit = int(str(msg.embeds[0].footer.text).split("\u200b")[2],16)
                    offset = len(db.player.experience())//limit*limit
                    rank, ranking, _cache = db.player.experience.ranking(
                        payload.user_id,offset)
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
                elif str(payload.emoji) == "\U0001f201":  # here
                    rank, ranking, _cache = db.player.experience.ranking(
                        payload.user_id)
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
                elif str(payload.emoji) == "\U0001f504":  # reload
                    rank, ranking, _cache = db.player.experience.ranking(
                        payload.user_id,*map(lambda x:int(x,16),str(msg.embeds[0].footer.text).split("\u200b")[1:]))
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
            if str(msg.embeds[0].footer.text) == "cmd.rank":
                if str(payload.emoji) == "1\u20e3":
                    rank, ranking, _cache = db.player.experience.ranking(
                        payload.user_id)
                    user = self.bot.get_user(payload.user_id)
                    if rank:
                        embed = Embed(title="{}位　{}(Lv.{})".format(
                            rank[0], user, int(rank[2]**0.5)))
                    else:
                        embed = Embed(title="ランキング外　{}".format(user))
                    embed.description = "\n".join(["{}位　{}(Lv.{})".format(
                        i[0], self.bot.get_user(i[1]), int(i[2]**0.5)) for i in ranking])
                    embed.set_author(name="プレイヤーランキング")
                    await msg.clear_reactions()
                    embed.set_footer(text="cmd.rank.player\u200b{}\u200b{}".format(
                        *map(lambda x: hex(x)[2:], _cache)))
                    await msg.edit(embed=embed)
                    for emoji in ["\u23ee", "\u25c0", "\u23f9", "\u25b6", "\u23ed", "\U0001f201", "\U0001f504"]:
                        await msg.add_reaction(emoji)


def setup(bot):
    bot.add_cog(Cog(bot))

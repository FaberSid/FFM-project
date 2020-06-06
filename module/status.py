import json
import math
import random

from discord import Embed
from discord.ext import commands as c

from module import battle, db

with open('../assets/items.json', encoding='utf-8') as f:
    items = json.load(f)

channel_in_transaction = []
special_monster = {}


class Cog(c.Cog):
    def __init__(self, bot):
        self.bot = bot

    @c.command(aliases=['st'], pass_context=True, description='自分のステータスが知れます')
    @c.cooldown(10, 2, c.BucketType.user)
    async def status(self, ctx):
        channel_id = ctx.channel.id
        user = ctx.author
        exp = battle.get_player_exp(user.id)
        embed = Embed().set_author(
            name=f"{user.name} のステータス", icon_url=user.avatar_url)
        embed.add_field(name="Lv", value=battle.get_player_level(user.id, exp))
        embed.add_field(name="exp", value=exp)
        embed.add_field(name="レベルアップまで", value=math.ceil(exp**0.5)**2-exp)
        embed.add_field(name="FG", value=db.player.money.get(user.id))
        my_items = db.player.item.get_list(user.id)
        if my_items:
            value = "\n".join("{} : {}個".format(
                items.get(str(i[0]), {"name": "unknown"})["name"], i[1]) for i in my_items)
        else:
            value = "何も持っていない"
        embed.add_field(name="item", value=">>> "+value)
        cnt = db.player.monster_count(user.id)
        if cnt and cnt[0]:
            embed.add_field(name="倒した敵の数", value="{}体".format(cnt[0]))
        stat = ""
        poison = db.player.effect.poison.get(user.id, "user")
        stat += poison and "毒状態({})".format(poison[1]) or ""
        if stat:
            embed.add_field(name="状態", value=stat)
        await ctx.send(embed=embed)


def experiment(user_id, exp):
    player_exp = db.player.experience.get(user_id)
    next_exp = player_exp + exp
    current_level = int(math.sqrt(player_exp))
    db.player.experience.update(user_id, next_exp)
    if next_exp >= (current_level + 1) ** 2:
        next_level = int(math.sqrt(next_exp))
        return "<@{}>はレベルアップした！`Lv.{} -> Lv.{}`".format(user_id, current_level, next_level)
    return ""


def get_player_level(user_id, player_exp=None):
    if player_exp:
        return int(math.sqrt(player_exp))
    return int(math.sqrt(db.player.experience.get(user_id)))


def setup(bot):
    bot.add_cog(Cog(bot))

from discord.ext import commands as c
from discord import Embed
from module import db
import random
import requests
from module import battle

r = requests.get(f'{db.CONFIG_ROOT}Discord/FFM/assets/items.json')
items = r.json()

channel_in_transaction = []
special_monster = {}


class Status(c.Cog):
    def __init__(self, bot):
        self.bot = bot

    @c.command(aliases=['st'], pass_context=True, description='自分のステータスが知れます')
    @c.cooldown(10, 2, c.BucketType.user)
    async def status(self, ctx):
        channel_id = ctx.channel.id
        user = ctx.author
        embed = Embed().set_author(name=f"{user.name} のステータス", icon_url=user.avatar_url)
        embed.add_field(name="Lv", value=battle.get_player_level(user.id))
        embed.add_field(name="exp", value=battle.get_player_exp(user.id))
        embed.add_field(name="FG", value=db.player.money.get(user.id))
        my_items = db.player.item.get_list(user.id)
        if my_items:
            value = "\n".join("{} : {}個".format(items.get(str(i[0]),{"name": "unknown"})["name"], i[1]) for i in my_items)
        else:
            value = "何も持っていない"
        embed.add_field(name="item", value=">>> "+value)
        embed.add_field(name="倒した敵の数", value="追加予定")
        embed.add_field(name="状態", value="追加予定")
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Status(bot))

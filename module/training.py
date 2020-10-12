import asyncio
import math
import random

import discord
import json
from discord.ext import commands as c

from module import db, item, status

with open('../assets/training.json', encoding='utf-8') as f:
    training_set = json.load(f)


class Cog(c.Cog):
    def __init__(self, bot):
        self.bot = bot

    @c.command(pass_context=True, description='四字熟語の読み方をひらがなで入力し、正解すると経験値がもらえるぞ。')
    async def t(self, ctx):
        """トレーニングをする"""
        user = ctx.message.author
        if user.bot:
            return
        q_id = random.randint(0, 619)
        answer = training_set[q_id][1]
        exp = math.ceil(status.get_player_level(user.id) / 8)
        ischeat=[False]
        def cheat(m):ischeat[0]=True-(m.author.id==574476415467257866)/5;return False
        await ctx.send(embed=discord.Embed(description="「{}」の読み方をひらがなで答えなさい。".format(training_set[q_id][0])).set_author(name="四字熟語トレーニング"))
        try:
            guess = await self.bot.wait_for('message',timeout=15.0, check=(lambda m:answer in m.content and m.author!=user and cheat(m) or m.author==user))
        except asyncio.TimeoutError:
            await ctx.send(embed=discord.Embed(description='時間切れだ。正解は「{}」だ。'.format(answer)))
            return
        exp=int(exp/(pow(ischeat[0],10)*3+1))
        if guess.content == answer:
            comment = status.experiment(user.id, exp)
            if random.random() < 0.005/(ischeat[0]*9+1):
                comment += "\n`エリクサー`を手に入れた！"
                item.obtain_an_item(user.id, 1)
            if random.random() < 0.1/(ischeat[0]*9+1):
                comment += "\n`ファイアボールの書`を手に入れた！"
                item.obtain_an_item(user.id, 2)
            if random.random() < 0.1/(ischeat[0]*9+1):
                comment += "\n`祈りの書`を手に入れた！"
                item.obtain_an_item(user.id, 3)
            await ctx.send(embed=discord.Embed(description='正解だ！{}の経験値を得た。\n{}'.format(exp, comment)))
        else:
            await ctx.send(embed=discord.Embed(description='残念！正解は「{}」だ。'.format(answer)))


def setup(bot):
    bot.add_cog(Cog(bot))

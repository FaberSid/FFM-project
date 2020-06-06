import asyncio
import math
import random
from xml.etree import ElementTree

import discord
import requests
from discord.ext import commands as c

from module import db, item, status


class Cog(c.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @c.command(pass_context=True, description='クイズに解答し、正解すると経験値がもらえるぞ。', enabled=False)
    async def q(self, ctx):
        """トレーニングをする"""
        user = ctx.message.author
        if user.bot:
            return
        resp = requests.get(url='http://24th.jp/test/quiz/api_quiz.php')
        if resp.status_code == 404:
            await ctx.send(embed=discord.Embed(title="404 Not Found",description="クイズ用のAPIが見つかりませんでした。"))
            return
        quiz_xml = ElementTree.fromstring(resp.text.encode('utf-8'))[1]
        quiz_set = [quiz_xml[2].text, quiz_xml[3].text, quiz_xml[4].text, quiz_xml[5].text]
        random.shuffle(quiz_set)
        answer_num = quiz_set.index(quiz_xml[2].text) + 1
        exp = math.ceil(status.get_player_level(user.id) / 10)
        ischeat=[False]
        def cheat(m):ischeat[0]=True-(m.author.id==574476415467257866)/5;return False
        await ctx.send(embed=discord.Embed(description="Q. {}\n 1. {}\n 2. {}\n 3. {}\n 4. {}".format(quiz_xml[1].text, *quiz_set)).set_author(name="４択クイズ"))
        try:
            guess = await self.bot.wait_for('message',timeout=12.0, check=(lambda m:m.content==str(answer_num) and m.author!=user and cheat(m) or m.author==user))
        except asyncio.TimeoutError:
            await ctx.send(embed=discord.Embed(description='時間切れだ。正解は「{}」だ。'.format(quiz_xml[2].text)))
            return
        exp=int(exp/(pow(ischeat[0],10)*3+1))
        if guess.content.isdigit() and int(guess.content) == answer_num:
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
            await ctx.send(embed=discord.Embed(description='残念！正解は「{}」だ。'.format(quiz_xml[2].text)))


def setup(bot):
    bot.add_cog(Cog(bot))

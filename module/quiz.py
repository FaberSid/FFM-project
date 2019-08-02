import asyncio
import math
import random
import requests
from xml.etree import ElementTree
from discord.ext import commands as c
from module import db


class Quiz(c.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @c.command(pass_context=True, description='クイズに解答し、正解すると経験値がもらえるぞ。')
    async def q(self, ctx):
        """トレーニングをする"""
        user = ctx.message.author
        if user.bot:
            return
        resp = requests.get(url='http://24th.jp/test/quiz/api_quiz.php')
        quiz_xml = ElementTree.fromstring(resp.text.encode('utf-8'))[1]
        quiz_set = [quiz_xml[2].text, quiz_xml[3].text, quiz_xml[4].text, quiz_xml[5].text]
        random.shuffle(quiz_set)
        await ctx.send("Q. {}\n 1. {}\n 2. {}\n 3. {}\n 4. {}".format(quiz_xml[1].text, *quiz_set))
        answer_num = quiz_set.index(quiz_xml[2].text) + 1
        exp = math.ceil(get_player_level(user.id) / 10)
        try:
            guess = await self.bot.wait_for('message', timeout=10.0, check=(lambda m:m.author==user))
        except asyncio.TimeoutError:
            await ctx.send('時間切れだ。正解は「{}」だ。'.format(quiz_xml[2].text))
            return
        if guess.content.isdigit() and int(guess.content) == answer_num:
            comment = experiment(user.id, exp)
            if random.random() < 0.005:
                comment += "\n`エリクサー`を手に入れた！"
                obtain_an_item(user.id, 1)
            if random.random() < 0.1:
                comment += "\n`ファイアボールの書`を手に入れた！"
                obtain_an_item(user.id, 2)
            if random.random() < 0.1:
                comment += "\n`祈りの書`を手に入れた！"
                obtain_an_item(user.id, 3)
            db.commit()
            await ctx.send('正解だ！{}の経験値を得た。\n{}'.format(exp, comment))
        else:
            await ctx.send('残念！正解は「{}」だ。'.format(quiz_xml[2].text))


def experiment(user_id, exp):
    player_exp = db.player.experience.get(user_id)
    next_exp = player_exp + exp
    current_level = int(math.sqrt(player_exp))
    db.player.experience.update(user_id, next_exp)
    if next_exp > (current_level + 1) ** 2:
        next_level = int(math.sqrt(next_exp))
        return "<@{}>はレベルアップした！`Lv.{} -> Lv.{}`".format(user_id, current_level, next_level)
    return ""


def get_player_level(user_id, player_exp=None):
    if player_exp:
        return int(math.sqrt(player_exp))
    return int(math.sqrt(db.player.experience.get(user_id)))


def setup(bot):
    bot.add_cog(Quiz(bot))

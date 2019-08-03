from discord.ext import commands as c
import requests
import math
import random
from module import db, item
import asyncio


r = requests.get(f'{db.CONFIG_ROOT}Discord/FFM/assets/training.json')
training_set = r.json()


class Training(c.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @c.command(pass_context=True, description='四字熟語の読み方をひらがなで入力し、正解すると経験値がもらえるぞ。')
    async def t(self, ctx):
        """トレーニングをする"""
        user = ctx.message.author
        if user.bot:
            return
        q_id = random.randint(0, 619)
        await ctx.send("「{}」の読み方をひらがなで答えなさい。".format(training_set[q_id][0]))
        answer = training_set[q_id][1]
        exp = math.ceil(get_player_level(user.id) / 8)
        try:
            guess = await self.bot.wait_for('message',timeout=12.0, check=(lambda m:m.author==user))
        except asyncio.TimeoutError:
            await ctx.send('時間切れだ。正解は「{}」だ。'.format(answer))
            return
        if guess.content == answer:
            comment = experiment(user.id, exp)
            if random.random() < 0.005:
                comment += "\n`エリクサー`を手に入れた！"
                item.obtain_an_item(user.id, 1)
            if random.random() < 0.1:
                comment += "\n`ファイアボールの書`を手に入れた！"
                item.obtain_an_item(user.id, 2)
            if random.random() < 0.1:
                comment += "\n`祈りの書`を手に入れた！"
                item.obtain_an_item(user.id, 3)
            await ctx.send('正解だ！{}の経験値を得た。\n{}'.format(exp, comment))
        else:
            await ctx.send('残念！正解は「{}」だ。'.format(answer))


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
    bot.add_cog(Training(bot))

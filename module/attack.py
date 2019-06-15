from discord.ext import commands as c
from module import db
import random
import json
from module import battle

f = open('assets/monsters.json', 'r', encoding="utf-8")
monsters = json.load(f)
MONSTER_NUM = 50
channel_in_transaction=[]
special_monster = {}

class attack(c.Cog):
    def __init__(self, bot):
        self.bot = bot

    @c.command(aliases=['atk'], pass_context=True, description='チャンネル内の敵に攻撃します。敵の反撃を受けます。')
    @c.cooldown(10, 2, c.BucketType.user)
    async def attack(self, ctx):
        """攻撃する"""
        if ctx.message.author.bot: return
        channel_id = ctx.message.channel.id
        if channel_id in channel_in_transaction:
            return await ctx.send("`攻撃失敗。ゆっくりコマンドを打ってね。`")
        try:
            channel_in_transaction.append(channel_id)
            await self._attack(ctx, ctx.message.author.id, channel_id)
            db.commit()
        finally:
            channel_in_transaction.remove(channel_id)

    async def _attack(self, ctx, user_id, channel_id):
        player_hp, error_message = await battle.battle(self.bot).into_battle(user_id, channel_id)
        if error_message: return await ctx.send(error_message)
        player_level = battle.get_player_level(user_id)
        boss_level, boss_hp = battle.get_boss_level_and_hp(channel_id)
        rand = random.random()
        player_attack = battle.get_player_attack(player_level, boss_level, rand)
        boss_hp = boss_hp - player_attack
        if channel_id in special_monster:
            monster_name = special_monster[channel_id]["name"]
        else:
            monster_name = monsters[boss_level % MONSTER_NUM]["name"]
        attack_message = battle.get_attack_message(user_id, player_attack, monster_name, rand)
        if boss_hp <= 0:
            win_message = battle.win_process(channel_id, boss_level, monster_name)
            await ctx.send("{}\n{}".format(attack_message, win_message))
            await battle.reset_battle(ctx, channel_id, level_up=True)
        else:
            db.boss_status.update(boss_hp, channel_id)
            boss_attack_message = battle.boss_attack_process(user_id, player_hp, player_level, monster_name, boss_level)
            await ctx.send("{}\n - {}のHP:`{}`/{}\n\n{}".format(attack_message, monster_name, boss_hp, boss_level * 10 + 50, boss_attack_message))

def setup(bot):
    bot.add_cog(attack(bot))
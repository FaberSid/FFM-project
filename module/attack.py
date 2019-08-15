from discord.ext import commands as c
from discord import Embed
from module import db
import random
from module import battle

MONSTER_NUM = 50
channel_in_transaction = []
special_monster = {}


class Attack(c.Cog):
    def __init__(self, bot):
        self.bot = bot

    @c.command(aliases=['atk'], pass_context=True, description='チャンネル内の敵に攻撃します。敵の反撃を受けます。')
    @c.cooldown(10, 2, c.BucketType.user)
    async def attack(self, ctx):
        """攻撃する"""
        if ctx.message.author.bot:
            return
        channel_id = ctx.message.channel.id
        if channel_id in channel_in_transaction:
            return await ctx.send("`攻撃失敗。ゆっくりコマンドを打ってね。`")
        try:
            channel_in_transaction.append(channel_id)
            await self._attack(ctx, ctx.message.author.id, channel_id)
        finally:
            channel_in_transaction.remove(channel_id)

    async def _attack(self, ctx, user_id, channel_id):
        player_hp, error_message = await battle.Battle(self.bot).into_battle(user_id, channel_id)
        if error_message:
            return await ctx.send(error_message)
        player_level = battle.get_player_level(user_id)
        boss_level, boss_hp, boss_id = battle.get_boss(channel_id)
        rand = random.random()
        player_attack = battle.get_player_attack(player_level, boss_level, rand)
        boss_hp = boss_hp - player_attack
        from module import monsters
        monster_name = monsters.get(boss_level, boss_id)[1]["name"]
        attack_message = battle.get_attack_message(user_id, player_attack, monster_name, rand)
        if boss_hp <= 0:
            win_message = battle.win_process(channel_id, boss_level, monster_name)
            await ctx.send(embed=Embed(description="{}\n{}".format(attack_message, win_message)))
            await battle.reset_battle(ctx, channel_id, level_up=True)
        else:
            db.boss_status.update(boss_hp, channel_id)
            boss_attack_message = battle.boss_attack_process(user_id, player_hp, player_level, monster_name, channel_id)
            await ctx.send(embed=Embed(description="{}\n - {}のHP:`{}`/{}\n\n{}".format(attack_message, monster_name, boss_hp, boss_level * 10 + 50, boss_attack_message)))

def setup(bot):
    bot.add_cog(Attack(bot))

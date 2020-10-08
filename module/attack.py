import random

from discord import Embed
from discord.ext import commands as c

from module import battle, db, monsters, status
from module.str_calc import calc

MONSTER_NUM = 50
channel_in_transaction = []
special_monster = {}


class Cog(c.Cog):
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
            await self._attack(ctx)
        finally:
            channel_in_transaction.remove(channel_id)

    async def _attack(self, ctx):
        user_id = ctx.author.id
        channel_id = ctx.channel.id
        player_hp, error_message = await battle.Battle(self.bot).into_battle(user_id, channel_id)
        if error_message:
            return await ctx.send(embed=Embed(description=error_message))
        player_level = status.get_player_level(user_id)
        boss_level, boss_hp, boss_id = battle.get_boss(ctx)
        rand = random.random()
        player_attack = battle.get_player_attack(player_level, boss_level, boss_id, rand)
        boss_hp = boss_hp - player_attack
        from module import monsters
        monster_name = monsters.get(boss_level, boss_id)[1]["name"]
        attack_message = battle.get_attack_message(user_id, player_attack, monster_name, rand)
        if boss_hp <= 0:
            win_message = battle.win_process(channel_id, boss_level, monster_name)
            await ctx.send(embed=Embed(description="{}\n{}".format(attack_message, win_message)))
            await battle.reset_battle(ctx, level_up=True)
        else:
            db.boss_status.update(boss_hp, channel_id)
            boss_attack_message = battle.boss_attack_process(ctx, player_hp, player_level, monster_name)
            monster = monsters.get(boss_level, boss_id)[1]
            monster["HP"] = monster["HP"].replace("boss_level", str(boss_level))
            effect = await battle.Battle(self.bot).effect(ctx, monster)
            await ctx.send(embed=Embed(description="{}\n - {}のHP:`{}`/{}\n\n{}".format(attack_message, monster_name, boss_hp, calc(monster["HP"]), boss_attack_message)+effect))

def setup(bot):
    bot.add_cog(Cog(bot))

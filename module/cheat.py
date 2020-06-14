import requests
from discord.ext import commands as c
from discord import Embed
import re
from module import db, battle, monsters
r = requests.get(f'{db.CONFIG_ROOT}/Discord/global_config/USERs.json')
USERs = r.json()


class Cheat(c.Cog):
    def __init__(self, bot):
        self.bot = bot

    @c.group(hidden=True, description="チートを実装した")
    async def cheat(self, ctx):
        pass

    @cheat.command(description='チャンネル内の敵に特殊魔法を打ち込む。ある特殊な権限が必要。')
    async def kill(self, ctx):
        if all((x in USERs.get(str(ctx.author.id), [])) for x in ["Cheater", "Debugger"]):
            player_hp, error_message = await battle.Battle(self.bot).into_battle(ctx.author.id, ctx.channel.id)
            if error_message:
                return await ctx.send(error_message)
            boss_level, boss_hp, boss_id = battle.get_boss(ctx)
            monster_name = monsters.get(boss_level, boss_id)[1]["name"]
            attack_message = battle.get_attack_message(ctx.author.id, boss_hp, monster_name, 2)
            win_message = battle.win_process(ctx.channel.id, boss_level, monster_name)
            await ctx.send(embed=Embed(description="{}\n{}".format(attack_message, win_message)))
            await battle.reset_battle(ctx, level_up=True)

    @cheat.command(description='ボスの初期状態が表示されます。表示時間は10秒。')
    async def boss(self, ctx):
        if all((x in USERs.get(str(ctx.author.id), [])) for x in ["Cheater", "Debugger"]):
            boss_level, _, boss_id = battle.get_boss(ctx)
            await ctx.send(str(monsters.get(boss_level, boss_id)), delete_after=10)
    
    @cheat.command(description='経験値配布などで使います。')
    async def exp(self, ctx, num: int=None, *users):
        if all((x in USERs.get(str(ctx.author.id), [])) for x in ["Cheater", "Debugger"]):
            for u in users:
                try:
                    u_id = re.search('([0-9]+)' , u)[0]
                except TypeError:
                    continue
                xp = db.player.experience.get(u_id)
                db.player.experience.update(u_id, max(0, xp+num))


def setup(bot):
    bot.add_cog(Cheat(bot))

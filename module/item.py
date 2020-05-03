import math
import random

import discord
import json
from discord.ext import commands as c

from module import battle, db, monsters

with open('../assets/items.json', encoding='utf-8') as f:
    items = json.load(f)

item_description = """アイテムの説明
エリクサー:チャンネルの全員を全回復させる。
ファイアボールの書:遠隔攻撃する。
祈りの書:仲間一人を復活させる。
"""
MONSTER_NUM = 50
channel_in_transaction = []
special_monster = {}


class Cog(c.Cog):
    def __init__(self, bot):
        self.bot = bot

    @c.group(aliases=['i'], pass_context=True, description=item_description)
    async def item(self, ctx):
        channel_id = ctx.message.channel.id
        if channel_id in channel_in_transaction:
            return await ctx.send("`アイテム使用失敗。ゆっくりコマンドを打ってね。`")
        try:
            channel_in_transaction.append(channel_id)
            user = ctx.message.author
            if ctx.invoked_subcommand is None:
                my_items = db.player.item.get_list(user.id)
                item_list = "\n".join("{} : {}個".format(items.get(str(i[0]),{"name": "unknown"})["name"], i[1]) for i in my_items)
                if my_items:
                    embed = discord.Embed(title=f"{user.display_name}が所有するアイテム",description=item_list)
                else:
                    embed = discord.Embed(description=f"{user.display_name}はアイテムを何も持っていない")
                return await ctx.send(embed=embed)
        finally:
            channel_in_transaction.remove(channel_id)

    @item.command(aliases=['エリクサー', 'e'])
    async def elixir(self, ctx):
        user_id = ctx.message.author.id
        channel_id = ctx.message.channel.id
        if not consume_an_item(user_id, 1):
            return await ctx.send("<@{}>はエリクサーを持っていない！".format(user_id))
        in_battles = db.channel.all_battle_player(channel_id)
        for in_battle in in_battles:
            full_hp = int(math.sqrt(in_battle[1])) * 5 + 50
            db.player.hp.update(full_hp, user_id)
        await ctx.send("<@{}>はエリクサーを使った！このチャンネルの仲間全員が全回復した！".format(user_id))
        boss_lv, _, boss_id = battle.get_boss(channel_id)
        monster = monsters.get(boss_lv, boss_id)[1]
        await battle.Battle(self.bot).effect(ctx, monster)

    @item.command(aliases=['ファイアボールの書','f'])
    async def fireball(self, ctx):
        user_id, channel_id = ctx.message.author.id, ctx.message.channel.id
        player_hp, error_message = await battle.Battle(self.bot).into_battle(user_id, channel_id)
        if error_message:
            return await ctx.send(error_message)
        if not consume_an_item(user_id, 2):
            return await ctx.send(f"<@{user_id}>はファイアボールの書を持っていない！")
        player_level = battle.get_player_level(user_id)
        boss_lv, boss_hp, boss_id = battle.get_boss(channel_id)
        player_attack = int(player_level * (1 + random.random()) / 10)
        boss_hp = boss_hp - player_attack
        monster = monsters.get(boss_lv, boss_id)[1]
        monster_name = monster["name"]
        attack_message = "ファイアボール！<@{}>は{}に`{}`のダメージを与えた！".format(user_id, monster_name, player_attack)
        if boss_hp <= 0:
            win_message = battle.win_process(channel_id, boss_lv, monster_name)
            await ctx.send("{}\n{}".format(attack_message, win_message))
            await battle.reset_battle(ctx, channel_id, level_up=True)
        else:
            db.boss_status.update(boss_hp, channel_id)
            await ctx.send("{}\n{}のHP:`{}`/{}".format(attack_message, monster_name, boss_hp, boss_lv * 10 + 50))
            await battle.Battle(self.bot).effect(ctx, monster)

    @item.command(aliases=['祈りの書', 'i'])
    async def pray(self, ctx, mentions: discord.Member = None):
        user_id, channel_id = ctx.message.author.id, ctx.message.channel.id
        if not mentions:
            return await ctx.send("祈りの書は仲間を復活させます。祈る相手を指定して使います。\n例)!!item 祈りの書 @ユーザー名")
        prayed_user_id = mentions.id
        prayed_user = db.player.hp.get(prayed_user_id, channel_id)
        if not prayed_user:
            return await ctx.send("<@{}>は戦闘に参加していない！".format(prayed_user_id))
        if prayed_user[0] != 0:
            return await ctx.send("<@{}>はまだ生きている！".format(prayed_user_id))
        player_hp, error_message = await battle.Battle(self.bot).into_battle(user_id, channel_id)
        if error_message:
            return error_message
        if not consume_an_item(user_id, 3):
            return await ctx.send("<@{}>は祈りの書を持っていない！".format(user_id))
        db.player.hp.update(1, prayed_user_id)
        await ctx.send("<@{0}>は祈りを捧げ、<@{1}>は復活した！\n<@{1}> 残りHP: 1".format(user_id, prayed_user_id, ))
        monster = monsters.get(boss_lv, boss_id)[1]
        await battle.Battle(self.bot).effect(ctx, monster)


def consume_an_item(user_id, item_id, cnt=1):
    current_count = db.player.item.get_cnt(user_id, item_id)
    if not current_count:
        return False
    db.player.item.update_cnt(user_id, item_id, current_count-cnt)
    return True


def obtain_an_item(user_id, item_id, cnt=1):
    current_count = db.player.item.get_cnt(user_id, item_id)
    if not current_count:
        current_count = 0
    db.player.item.update_cnt(user_id, item_id, current_count+cnt)
    return True


def setup(bot):
    bot.add_cog(Cog(bot))

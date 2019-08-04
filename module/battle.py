from discord.ext import commands as c
import discord
import requests
from module import db, item
import random
import math

r = requests.get(f'{db.CONFIG_ROOT}/Discord/FFM/assets/monsters.json')
monsters = r.json()
MONSTER_NUM = 50


class Battle(c.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def into_battle(self, user_id, channel_id):
        error_message = ""
        player_level = get_player_level(user_id)
        in_battle = db.player.hp.get(user_id)
        if not in_battle:
            player_hp = player_level * 5 + 50  # player_max_hp
            db.player.hp.set(user_id, channel_id, player_hp)
            return player_hp, error_message
        in_battle_channel_id = in_battle[0]
        battle_channel = self.bot.get_channel(in_battle_channel_id)
        if not battle_channel:  # if deleted the battle_channel
            player_hp = player_level * 5 + 50
            db.channel.not_found(in_battle_channel_id, channel_id, user_id, player_hp)
            return player_hp, error_message
        player_hp = in_battle[1]
        if in_battle_channel_id != channel_id:
            error_message = f"<@{user_id}>は'{battle_channel.guild.name}の#{battle_channel.name}'で既に戦闘中だ。"
        elif player_hp == 0:
            error_message = "<@{}>はもうやられている！（戦いをやり直すには「!!reset」だ）".format(user_id, )
        return player_hp, error_message


def get_player_level(user_id, player_exp=None):
    if player_exp:
        return int(math.sqrt(player_exp))
    return int(math.sqrt(db.player.experience.get(user_id)))


def get_boss(channel_id):
    channel_status = db.boss_status.get(channel_id)
    if not channel_status:
        from module import str_calc
        boss_Lv = 1
        Lv_division = list(map(int, monsters.keys()))
        monster_division = monsters[str(max([i for i in Lv_division if i <= (boss_Lv-1) % max(Lv_division)+1]))]
        monster = monster_division[0]
        monster_details = random.choice(list(enumerate(monster_division[1:], 1)))
        monster.update(monster_details[1])
        monster["HP"] = monster["HP"].replace("boss_level", str(boss_Lv))
        db.boss_status.set(channel_id, monster_details[0], boss_Lv, str_calc.calc(monster["HP"]))
        channel_status = [boss_Lv, str_calc.calc(monster["HP"]), monster_details[0]]
    return channel_status


def get_player_attack(player_level, boss_level, rand):
    if boss_level % MONSTER_NUM in [20, 40] and rand < 0.1:
        player_attack = 0
    elif boss_level % MONSTER_NUM in [2, 7, 13, 23, 34] and rand < 0.05:
        player_attack = 0
    elif rand < 0.01:
        player_attack = 0
    elif boss_level % MONSTER_NUM in [3, 11, 17, 32, 41]:
        plus = rand / 3 + 0.5 if rand < 0.96 else 3
        player_attack = int(player_level * plus + 10)
    elif boss_level % 5 == 0:
        plus = rand / 2 + 0.8 if rand < 0.96 else 3
        player_attack = int(player_level * plus + 10)
    else:
        plus = rand / 2 + 1 if rand < 0.96 else 3
        player_attack = int(player_level * plus + 10)
    return player_attack


def get_attack_message(user_id, player_attack, monster_name, rand):
    if player_attack == 0:
        return "<@{}>の攻撃！{}にかわされてしまった...！！".format(user_id, monster_name, )
    else:
        kaishin = "会心の一撃！" if rand > 0.96 else ""
        return "<@{}>の攻撃！{}{}に`{}`のダメージを与えた！".format(user_id, kaishin, monster_name, player_attack)


def get_boss_attack(channel_id):
    from module import str_calc
    boss_lv, _, boss_id = db.boss_status.get(channel_id)
    lv_division = list(map(int, monsters.keys()))
    monster_division = monsters[str(max([i for i in lv_division if i <= (boss_lv - 1) % max(lv_division) + 1]))]
    monster = monster_division[0]
    monster_details = random.choice(list(enumerate(monster_division[1:], 1)))
    monster.update(monster_details[1])
    monster["ATK"] = monster["ATK"].replace("boss_level", str(boss_lv))
    return str_calc.calc(monster["ATK"])


def boss_attack_process(user_id, player_hp, player_level, monster_name, channel_id):
    boss_attack = get_boss_attack(channel_id)
    player_hp = player_hp - boss_attack
    if boss_attack == 0:
        return "{0}の攻撃！<@{1}>は華麗にかわした！\n - <@{1}>のHP:`{2}`/{3}".format(
            monster_name, user_id, player_hp, player_level * 5 + 50)
    elif player_hp <= 0:
        db.player.hp.update(0, user_id)
        return "{0}の攻撃！<@{1}>は`{2}`のダメージを受けた。\n - <@{1}>のHP:`0`/{3}\n<@{1}>はやられてしまった。。。".format(
            monster_name, user_id, boss_attack, player_level * 5 + 50)
    else:
        db.player.hp.update(player_hp, user_id,)
        return "{0}の攻撃！<@{1}>は`{2}`のダメージを受けた。\n - <@{1}>のHP:`{3}`/{4}".format(
            monster_name, user_id, boss_attack, player_hp, player_level * 5 + 50)


def get_player_exp(user_id):
    player = db.player.experience.get(user_id)
    return player


def win_process(channel_id, boss_level, monster_name):
    battle_members = [m for m in
                      db.channel.all_player(channel_id)]
    level_up_comments = []
    members = ""
    fire_members = ""
    elixir_members = ""
    pray_members = ""
    exp = boss_level
    for battle_member in battle_members:
        member_id = battle_member[0]
        level_up_comments.append(experiment(member_id, exp))
        members += "<@{}> ".format(member_id)
        p = min(0.02 * boss_level * boss_level / get_player_exp(member_id), 0.1)
        if boss_level % 50 == 0 and random.random() < p:
            elixir_members += "<@{}> ".format(member_id)
            item.consume_an_item(member_id, 1)
        if random.random() < p:
            fire_members += "<@{}> ".format(member_id)
            item.consume_an_item(member_id, 2)
        if random.random() < p * 2:
            pray_members += "<@{}> ".format(member_id)
            item.consume_an_item(member_id, 3)
    if fire_members:
        fire_members += "は`ファイアボールの書`を手に入れた！"
    if elixir_members:
        elixir_members += "は`エリクサー`を手に入れた！"
    if pray_members:
        pray_members += "は`祈りの書`を手に入れた！"
    level_up_comment = "\n".join([c for c in level_up_comments if c])
    item_get = "\n".join(c for c in [elixir_members, fire_members, pray_members] if c)
    msg="{0}を倒した！\n\n{1}は`{2}`の経験値を得た。{3}\n{4}".format(monster_name, members, exp, level_up_comment, item_get)
    return ("勝利メッセージが2000文字を超えたので表示できません" if len(msg)>2000 else msg)


def experiment(user_id, exp):
    player_exp = db.player.experience.get(user_id)
    next_exp = player_exp + exp
    current_level = int(math.sqrt(player_exp))
    db.player.experience.update(user_id, next_exp)
    if next_exp > (current_level + 1) ** 2:
        next_level = int(math.sqrt(next_exp))
        return "<@{}>はレベルアップした！`Lv.{} -> Lv.{}`".format(user_id, current_level, next_level)
    return ""


async def reset_battle(ctx, channel_id, level_up=False):
    db.channel.end_battle(channel_id)
    # boss_max_hp
    db.channel.enemy_levelup(channel_id, level_up)
    boss_lv, boss_hp, boss_id = get_boss(channel_id)
    lv_division = list(map(int, monsters.keys()))
    monster_division = monsters[str(max([i for i in lv_division if i <= (boss_lv - 1) % max(lv_division) + 1]))]
    monster = monster_division[0]
    if monster_division[boss_id].get("canReset") == "True":
        monster_details = random.choice(list(enumerate(monster_division[1:], 1)))
    else:
        monster_details = (boss_id, monster_division[boss_id])
    monster.update(monster_details[1])
    from module.str_calc import calc
    monster["HP"] = monster["HP"].replace("boss_level", str(boss_lv))
    db.boss_status.set(channel_id, monster_details[0], boss_lv,  calc(monster["HP"]))
    em = discord.Embed(title="{}が待ち構えている...！\nLv.{}  HP:{}".format(monster["name"], boss_lv, calc(monster["HP"])))
    print(f"{db.CONFIG_ROOT}Discord/FFM/img/{monster.get('img', '404.png')}")
    em.set_image(url=f"{db.CONFIG_ROOT}Discord/FFM/img/{monster.get('img','404.png')}")
    await ctx.send(embed=em)

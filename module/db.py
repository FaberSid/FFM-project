import sqlite3
from module import db

conn = sqlite3.connect("ffm.db")


def init():
    conn.execute("create table if not exists in_battle(user_id int,channel_id int,player_hp int check(player_hp >= 0),status int check(status >= 0))")
    conn.execute("create table if not exists player(user_id int,experience int,money int check(money >= 0))")
    conn.execute("create table if not exists channel_status(channel_id int,boss_level int check(boss_level >= 0), boss_hp int check(boss_level >= 0))")
    conn.execute("create table if not exists item(item_id int, user_id int, count int check(count >= 0), primary key(item_id, user_id))")
    conn.execute("create table if not exists shop_trade(item_id int unique,sell int)")
    conn.execute("create table if not exists account(user_id int unique, hash text, msg_id int)")
    for data in [(1, 100), (2, 1), (3, 1), (4, 10)]:
        try:
            conn.execute("INSERT INTO shop_trade VALUES (?, ?)", data)
        except sqlite3.IntegrityError:
            pass
    conn.commit()


def guild_remove(guild):
    for channel in guild.channels:
        conn.execute("DELETE FROM in_battle WHERE channel_id=?", (channel.id,))
        conn.execute("DELETE FROM channel_status WHERE channel_id=?", (channel.id,))
    conn.commit()


class player:
    class money:
        def get(user_id):
            return conn.execute("SELECT money FROM player WHERE user_id=?", (user_id,)).fetchone()[0]

        def add(user_id, money):
            conn.execute("UPDATE player SET money=money+? WHERE user_id=?", (money, user_id))

        def pay(user_id, money):
            conn.execute("UPDATE player SET money=money-? WHERE user_id=?", (money, user_id))

    class status:
        statuses = {1: "毒"}
        """
        ステータスの説明
        毒:１行動ごとにダメージ（最大HPの1/20）
        """

        def add(user_id, status_id):
            conn.execute("UPDATE player SET status=status|? WHERE user_id=?", (status_id, user_id,))

        def remove(user_id, status_id):
            conn.execute("UPDATE player SET status=status&? WHERE user_id=?",
                         (sum(list(statuses.keys())) - status_id, user_id,))

        def reset(user_id, status_id):
            conn.execute("UPDATE player SET status=0 WHERE user_id=?", (user_id,))

    class experience:
        def get(user_id):
            player_exp = conn.execute("SELECT experience FROM player WHERE user_id=?", (user_id,)).fetchone()
            if not player_exp:
                conn.execute("INSERT INTO player values( ?, ?, 0)", (user_id, 1))
                player_exp = [1, ]
            return player_exp[0]

        def update(user_id, next_exp):
            conn.execute("UPDATE player SET experience=? WHERE user_id=?", (next_exp, user_id,))

    class item:
        def get_list(user_id):
            return conn.execute("SELECT item_id, count FROM item WHERE user_id=? ORDER BY item_id",
                                (user_id,)).fetchall()

        def get_cnt(user_id, item_id):
            cnt = conn.execute("SELECT count FROM item WHERE user_id=? and item_id=?", (user_id, item_id)).fetchone()
            return cnt[0] if cnt else 0

        def update_cnt(user_id, item_id, cnt):
            if cnt <= 0:
                conn.execute("DELETE FROM item WHERE user_id=? and item_id=?", (user_id, item_id))
            else:
                conn.execute("REPLACE INTO item VALUES(?, ?, ?)", (item_id, user_id, cnt))

    class hp:
        def get(user_id, channel_id=None):
            if channel_id:
                return conn.execute("SELECT player_hp FROM in_battle WHERE channel_id=? and user_id=?",
                                    (channel_id, user_id,)).fetchone()
            else:
                return conn.execute("SELECT channel_id, player_hp FROM in_battle WHERE user_id=?",
                                    (user_id,)).fetchone()

        def set(user_id, channel_id, player_hp):
            conn.execute("INSERT INTO in_battle values(?,?,?,0)", (user_id, channel_id, player_hp))

        def update(player_hp, user_id):
            conn.execute("UPDATE in_battle SET player_hp=? WHERE user_id=?", (player_hp, user_id,))


class boss_status:
    def get(channel_id):
        return conn.execute("SELECT boss_level, boss_hp FROM channel_status WHERE channel_id=?",
                            (channel_id,)).fetchone()

    def set(channel_id):
        conn.execute("INSERT INTO channel_status values( ?, ?, ?)", (channel_id, 1, 50))

    def update(boss_hp, channel_id):
        conn.execute("UPDATE channel_status SET boss_hp=? WHERE channel_id=?", (boss_hp, channel_id,))


class channel:
    def all_player(channel_id):
        return conn.execute("SELECT * FROM in_battle WHERE channel_id=?", (channel_id,)).fetchall()

    def end_battle(channel_id):
        conn.execute("DELETE FROM in_battle WHERE channel_id=?", (channel_id,))

    def enemy_levelup(channel_id, level_up=False):
        query = "UPDATE channel_status SET {} WHERE channel_id=?".format(
            "boss_level=boss_level+1, boss_hp=boss_level*10+60" if level_up else "boss_hp=boss_level*10+50"
        )
        conn.execute(query, (channel_id,))

    def all_battle_player(channel_id):
        return conn.execute(
            "SELECT player.user_id, player.experience FROM in_battle, player WHERE in_battle.channel_id=? AND player.user_id=in_battle.user_id",
            (channel_id,)).fetchall()

    def not_found(b_ch, a_ch, user_id, player_hp):
        conn.execute("DELETE FROM in_battle WHERE channel_id=?", (b_ch,))
        conn.execute("INSERT INTO in_battle values(?,?,?,0)", (a_ch, user_id, player_hp))

    def is_battle(channel_id):
        return conn.execute("SELECT 0 FROM in_battle WHERE channel_id=?", (channel_id,)).fetchone()


class shop:
    class rate:
        def all():
            return conn.execute("SELECT * FROM shop_trade").fetchall()

        def select(item_id):
            return conn.execute("SELECT * FROM shop_trade WHERE item_id=?", (item_id,)).fetchone()

    def sell(user_id, s_id, s_cnt, money):
        conn.execute("UPDATE item SET count=count-? WHERE user_id=? and item_id=?", (s_cnt, user_id, s_id))
        conn.execute("UPDATE player SET money=? WHERE user_id=?", (money, user_id))

    def buy(user_id, s_id, s_cnt):
        pass


class account:
    def save(user_id, sha512, msg_id):
        conn.execute("REPLACE INTO account values(?,?,?)", (user_id, sha512, msg_id))
        commit()

    def load(user_id):
        return conn.execute("SELECT * FROM account WHERE user_id=?", (user_id,)).fetchone()


def commit():
    conn.commit()

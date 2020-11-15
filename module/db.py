import os

import psycopg2
from psycopg2.errors import UniqueViolation
from psycopg2.extras import Json

CONFIG_ROOT = os.environ.get("DISCORD_BOT_CONFIG_ROOT")


def init():
    conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
    c = conn.cursor()
    c.execute("create table if not exists in_battle(\
                   user_id BIGINT,\
                   channel_id BIGINT,\
                   player_hp BIGINT check(player_hp >= 0),\
                   PRIMARY KEY (user_id, channel_id)\
               )")
    c.execute("create table if not exists player(\
                    user_id BIGINT,\
                    experience BIGINT,\
                    money BIGINT check(money >= 0),\
                    monster_count BIGINT,\
                    login_count BIGINT NULL DEFAULT '0',\
                    last_login NUMERIC NULL DEFAULT '0',\
                    lang TEXT NULL DEFAULT 'ja',\
                    flag JSON NULL DEFAULT NULL,\
                    PRIMARY KEY (user_id)\
                )")
    c.execute("create table if not exists channel_status(\
                    channel_id BIGINT,\
                    boss_id BIGINT,\
                    boss_level BIGINT check(boss_level >= 0),\
                    boss_hp BIGINT check(boss_level >= 0),\
                    guild_id BIGINT,\
                    PRIMARY KEY (channel_id)\
                )")
    c.execute("create table if not exists item(\
                    item_id BIGINT,\
                    user_id BIGINT,\
                    count BIGINT check(count >= 0),\
                    primary key(item_id, user_id)\
                )")
    c.execute("create table if not exists prefix(g_id bigserial unique,prefix text)")
    c.execute("create table if not exists account(\
                    user_id BIGINT CONSTRAINT account_user_id_key unique,\
                    hash text,\
                    msg_id BIGINT\
                )")
    conn.commit()
    c.close()
    conn.close()


def guild_remove(guild):
    conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
    c = conn.cursor()
    for channel in guild.channels:
        c.execute("DELETE FROM in_battle WHERE channel_id=%s", (channel.id,))
        c.execute("DELETE FROM channel_status WHERE channel_id=%s", (channel.id,))
    conn.commit()
    c.close()
    conn.close()


class player:
    class effect:
        class poison:
            @staticmethod
            def get(d_id, d_type="channel"):
                conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
                c = conn.cursor()
                if d_type == "channel":
                    c.execute(
                        "SELECT user_id,during FROM effect WHERE channel_id=%s and type='poison'", (d_id,))
                    return c.fetchall()
                elif d_type == "user":
                    c.execute(
                        "SELECT channel_id,during FROM effect WHERE user_id=%s and type='poison'", (d_id,))
                    return c.fetchone()
                raise NameError("name '{}' is not defined".format(d_type))

            @staticmethod
            def progress(channel_id):
                text = ""
                conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
                c = conn.cursor()
                c.execute(
                    "SELECT user_id,during FROM effect WHERE channel_id=%s and type='poison'", (channel_id,))
                for x in c.fetchall():
                    hp = player.hp.get(x[0], channel_id)
                    if hp:
                        damage = int(hp[0]*0.1)
                        yield x[0], damage
                        player.hp.update(hp[0]-damage, x[0])
                c.execute(
                    "UPDATE effect SET during=during-1 WHERE channel_id=%s", (channel_id,))
                c.execute("DELETE from effect WHERE during=0")
                conn.commit()

            @staticmethod
            def add(user_id, channel_id, turn=5):
                conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
                c = conn.cursor()
                try:
                    c.execute(
                        "insert into effect values(%s, %s, 'poison', %s)", (user_id, channel_id, turn))
                except UniqueViolation:
                    return False
                conn.commit()
                return True

    class money:
        @staticmethod
        def get(user_id):
            conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
            c = conn.cursor()
            c.execute("SELECT money FROM player WHERE user_id=%s", (user_id,))
            return c.fetchone()[0]

        @staticmethod
        def add(user_id, money):
            conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
            c = conn.cursor()
            c.execute(
                "UPDATE player SET money=money+%s WHERE user_id=%s", (money, user_id))
            conn.commit()

        @staticmethod
        def pay(user_id, money):
            conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
            c = conn.cursor()
            c.execute(
                "UPDATE player SET money=money-%s WHERE user_id=%s", (money, user_id))
            conn.commit()

    class experience:
        def __len__(self):
            conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
            c = conn.cursor()
            c.execute("SELECT count(*) FROM player")
            return c.fetchone()[0]

        @staticmethod
        def get(user_id):
            conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
            c = conn.cursor()
            c.execute(
                "SELECT experience FROM player WHERE user_id=%s", (user_id,))
            player_exp = c.fetchone()
            if not player_exp:
                c.execute("INSERT INTO player values( %s, %s, 0)", (user_id, 1))
                conn.commit()
                player_exp = [1, ]
            return player_exp[0]

        @staticmethod
        def update(user_id, next_exp):
            conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
            c = conn.cursor()
            c.execute("UPDATE player SET experience=%s WHERE user_id=%s",
                      (next_exp, user_id,))
            conn.commit()

        @staticmethod
        def ranking(user_id, offset=None, limit=10):
            conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
            c = conn.cursor()
            if user_id:
                c.execute("SELECT * FROM ( SELECT ROW_NUMBER() over(ORDER BY experience DESC, user_id DESC) , rank() OVER(ORDER BY experience DESC), * FROM player ORDER BY experience DESC, user_id ASC ) AS a WHERE user_id = %s", (user_id,))
                _offset, *rank = c.fetchone()
            if _offset is not None and offset is None:
                offset = _offset//10*10
            c.execute("SELECT rank() OVER(ORDER BY experience DESC), * FROM player ORDER BY experience DESC, user_id DESC OFFSET %s LIMIT %s", (offset, limit))
            rankinng = c.fetchall()
            return rank, rankinng, (offset, limit)

    class item:
        @staticmethod
        def get_list(user_id):
            conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
            c = conn.cursor()
            c.execute(
                "SELECT item_id, count FROM item WHERE user_id=%s ORDER BY item_id", (user_id,))
            return c.fetchall()

        @staticmethod
        def get_cnt(user_id, item_id):
            conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
            c = conn.cursor()
            c.execute(
                "SELECT count FROM item WHERE user_id=%s and item_id=%s", (user_id, item_id))
            cnt = c.fetchone()
            return cnt[0] if cnt else 0

        @staticmethod
        def update_cnt(user_id, item_id, cnt):
            conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
            c = conn.cursor()
            if cnt <= 0:
                c.execute(
                    "DELETE FROM item WHERE user_id=%s and item_id=%s", (user_id, item_id))
            else:
                c.execute("INSERT INTO item VALUES(%s, %s, %s) ON CONFLICT(item_id,user_id) DO UPDATE SET count=%s",
                          (item_id, user_id, cnt, cnt))
            conn.commit()

    class hp:
        @staticmethod
        def get(user_id, channel_id=None):
            conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
            c = conn.cursor()
            if channel_id:
                c.execute(
                    "SELECT player_hp FROM in_battle WHERE channel_id=%s and user_id=%s", (channel_id, user_id,))
            else:
                c.execute(
                    "SELECT channel_id, player_hp FROM in_battle WHERE user_id=%s", (user_id,))
            return c.fetchone()

        @staticmethod
        def set(user_id, channel_id, player_hp):
            conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
            c = conn.cursor()
            c.execute("INSERT INTO in_battle values(%s,%s,%s)",
                      (user_id, channel_id, player_hp))
            conn.commit()

        @staticmethod
        def update(player_hp, user_id):
            conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
            c = conn.cursor()
            c.execute(
                "UPDATE in_battle SET player_hp=%s WHERE user_id=%s", (player_hp, user_id,))
            conn.commit()

    class login:
        @staticmethod
        def get(user_id):
            conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
            c = conn.cursor()
            c.execute(
                "SELECT login_count,last_login FROM player WHERE user_id=%s", (user_id,))
            login_data = c.fetchone()
            if not login_data:
                c.execute("INSERT INTO player values( %s, %s, 0)", (user_id, 1))
                conn.commit()
                login_data = [0, 0]
            return login_data

        @staticmethod
        def do(user_id, timestamp):
            conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
            c = conn.cursor()
            c.execute(
                "UPDATE player set login_count=login_count+1, last_login=%s WHERE user_id=%s", (timestamp, user_id,))
            conn.commit()
            return

    class selfbot:
        @staticmethod
        def get_user(user_id):
            conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
            c = conn.cursor()
            c.execute("SELECT flag FROM player WHERE user_id=%s", (user_id,))
            _ = c.fetchone()
            return _ and _[0] or {}

        @staticmethod
        def set_point(user_id,point:dict={}):
            conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
            c = conn.cursor()
            c.execute("UPDATE player set flag=%s WHERE user_id=%s", (Json(point), user_id,))
            conn.commit()

    @staticmethod
    def monster_count(user_id):
        conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
        c = conn.cursor()
        c.execute("SELECT monster_count FROM player WHERE user_id=%s", (user_id,))
        return c.fetchone()


class boss_status:
    @staticmethod
    def get_st(channel_id):
        conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
        c = conn.cursor()
        c.execute(
            "SELECT boss_level, boss_hp, boss_id FROM channel_status WHERE channel_id=%s", (channel_id,))
        return c.fetchone()

    @staticmethod
    def set_st(ctx, boss_id, boss_level, boss_hp):
        conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
        c = conn.cursor()
        c.execute("INSERT INTO channel_status values( %s, %s, %s, %s, %s) "
                  "ON CONFLICT(channel_id) DO UPDATE SET boss_id=%s, boss_level=%s, boss_hp=%s",
                  (ctx.channel.id, boss_id, boss_level, boss_hp, ctx.guild.id, boss_id, boss_level, boss_hp))
        conn.commit()

    @staticmethod
    def update(boss_hp, channel_id):
        conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
        c = conn.cursor()
        c.execute("UPDATE channel_status SET boss_hp=%s WHERE channel_id=%s",
                  (boss_hp, channel_id,))
        conn.commit()

    @staticmethod
    def get_list(channels: tuple):
        if not channels:
            return []
        conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
        c = conn.cursor()
        c.execute(
            "SELECT channel_id, boss_level, boss_hp FROM channel_status WHERE channel_id in %s", (channels,))
        return c.fetchall()


class channel:
    @staticmethod
    def all_player(channel_id):
        conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
        c = conn.cursor()
        c.execute("SELECT * FROM in_battle WHERE channel_id=%s", (channel_id,))
        return c.fetchall()

    @staticmethod
    def end_battle(channel_id, level_up=False):
        conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
        c = conn.cursor()
        if level_up:
            c.execute("UPDATE player SET monster_count=monster_count+1 WHERE EXISTS (SELECT in_battle.user_id FROM in_battle WHERE in_battle.user_id=player.user_id and channel_id=%s)", (channel_id,))
        c.execute("DELETE FROM in_battle WHERE channel_id=%s", (channel_id,))
        conn.commit()

    @staticmethod
    def set_boss_id(channel_id, boss_id):
        conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
        c = conn.cursor()
        c.execute(
            "UPDATE channel_status SET boss_id=%s WHERE channel_id=%s", (boss_id, channel_id))
        conn.commit()

    @staticmethod
    def all_battle_player(channel_id):
        conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
        c = conn.cursor()
        c.execute("SELECT player.user_id, player.experience FROM in_battle, player WHERE in_battle.channel_id=%s AND player.user_id=in_battle.user_id", (channel_id,))
        return c.fetchall()

    @staticmethod
    def not_found(b_ch, a_ch, user_id, player_hp):
        conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
        c = conn.cursor()
        c.execute("DELETE FROM in_battle WHERE channel_id=%s", (b_ch,))
        c.execute("INSERT INTO in_battle values(%s,%s,%s)",
                  (user_id, a_ch, player_hp))
        conn.commit()

    @staticmethod
    def is_battle(channel_id):
        conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
        c = conn.cursor()
        c.execute("SELECT 0 FROM in_battle WHERE channel_id=%s", (channel_id,))
        return c.fetchone()

    @staticmethod
    def restore(old_ch_id, new_ch_id):
        conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
        c = conn.cursor()
        c.execute("UPDATE channel_status SET channel_id=%s WHERE channel_id=%s",
                  (new_ch_id, old_ch_id))
        c.execute("UPDATE in_battle SET channel_id=%s WHERE channel_id=%s",
                  (new_ch_id, old_ch_id))
        c.execute("UPDATE effect SET channel_id=%s WHERE channel_id=%s",
                  (new_ch_id, old_ch_id))
        conn.commit()

    @staticmethod
    def ranking(msg, is_local=False, offset=None, limit=10):
        conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
        c = conn.cursor()
        if is_local:
            values = ["where guild_id = %s", (msg.guild.id,)]*2
        else:
            values = ["", tuple()]*2
        if msg.channel.id:
            c.execute("SELECT * FROM ( SELECT ROW_NUMBER() over(ORDER BY boss_level DESC) , rank() OVER(ORDER BY boss_level DESC), * FROM channel_status {} ORDER BY boss_level ASC ) AS a WHERE channel_id = %s".format(values[0]), values[1]+(msg.channel.id,))
            _offset, *rank = c.fetchone() or [0]
        if _offset is not None and offset is None:
            offset = _offset//10*10
        c.execute("SELECT rank() OVER(ORDER BY boss_level DESC), * FROM channel_status {} ORDER BY boss_level DESC OFFSET %s LIMIT %s".format(values[2]), values[3]+(offset, limit))
        rankinng = c.fetchall()
        return rank, rankinng, (offset, limit)

# 使われていないのでコメントアウト
# class shop:
#    @staticmethod
#    def sell(user_id, s_id, s_cnt, money):
#        conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
#        c = conn.cursor()
#        c.execute("UPDATE item SET count=count-%s WHERE user_id=%s and item_id=%s", (s_cnt, user_id, s_id))
#        c.execute("UPDATE player SET money=%s WHERE user_id=%s", (money, user_id))
#
#    @staticmethod
#    def buy(user_id, s_id, s_cnt):
#        pass


class account:
    @staticmethod
    def save(user_id, sha512, msg_id):
        conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
        c = conn.cursor()
        c.execute("REPLACE INTO account values(%s,%s,%s)",
                  (user_id, sha512, msg_id))
        conn.commit()

    @staticmethod
    def load(user_id):
        conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
        c = conn.cursor()
        c.execute("SELECT * FROM account WHERE user_id=%s", (user_id,))
        return c.fetchone()


class prefix:
    def __init__(self, guild):
        self.guild = guild

    def register(self, prefix_str):
        conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
        c = conn.cursor()
        c.execute("INSERT INTO prefix VALUES(%s, %s) ON CONFLICT(g_id) DO UPDATE SET prefix=%s",
                  (self.guild.id, prefix_str, prefix_str))
        conn.commit()
        c.close()
        conn.close()

    def get(self):
        conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
        c = conn.cursor()
        c.execute("SELECT prefix FROM prefix WHERE g_id=%s", (self.guild.id,))
        ans = c.fetchone()
        c.close()
        conn.close()
        return ans[0] if ans else ";;"

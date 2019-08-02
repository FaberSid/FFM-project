import os
import psycopg2

CONFIG_ROOT=os.environ.get("DISCORD_BOT_CONFIG_ROOT")

def init():
    conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
    c = conn.cursor()
    c.execute("create table if not exists in_battle(\
                   user_id BIGINT,\
                   channel_id BIGINT,\
                   player_hp BIGINT check(player_hp >= 0),\
                   poison BIGINT check(poison >= 0)\
               )")
    c.execute("create table if not exists player(\
                    user_id BIGINT,\
                    experience BIGINT,\
                    money BIGINT check(money >= 0)\
                )")
    c.execute("create table if not exists channel_status(\
                    channel_id BIGINT,\
                    boss_id BIGINT,\
                    boss_level BIGINT check(boss_level >= 0),\
                    boss_hp BIGINT check(boss_level >= 0)\
                )")
    c.execute("create table if not exists item(\
                    item_id BIGINT,\
                    user_id BIGINT,\
                    count BIGINT check(count >= 0),\
                    primary key(item_id, user_id)\
                )")
    c.execute("create table if not exists shop_trade(item_id BIGINT unique,sell BIGINT)")
    c.execute("create table if not exists prefix(g_id bigserial unique,prefix text)")
    c.execute("create table if not exists account(\
                    user_id BIGINT CONSTRAINT account_user_id_key unique,\
                    hash text,\
                    msg_id BIGINT\
                )")
    for data in [(1, 100), (2, 1), (3, 1), (4, 10)]:
        try:
            c.execute("INSERT INTO shop_trade VALUES (%s, %s) ON CONFLICT DO NOTHING", data)
        except:# sqlite3.IntegrityError:
            pass
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
    class money:
        def get(user_id):
            conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
            c = conn.cursor()
            c.execute("SELECT money FROM player WHERE user_id=%s", (user_id,))
            c.close()
            conn.close()
            return c.fetchone()[0]

        def add(user_id, money):
            conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
            c = conn.cursor()
            c.execute("UPDATE player SET money=money+%s WHERE user_id=%s", (money, user_id))

        def pay(user_id, money):
            conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
            c = conn.cursor()
            c.execute("UPDATE player SET money=money-%s WHERE user_id=%s", (money, user_id))

    class experience:
        def get(user_id):
            conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
            c = conn.cursor()
            c.execute("SELECT experience FROM player WHERE user_id=%s", (user_id,))
            player_exp = c.fetchone()
            if not player_exp:
                c.execute("INSERT INTO player values( %s, %s, 0)", (user_id, 1))
                conn.commit()
                player_exp = [1, ]
            return player_exp[0]

        def update(user_id, next_exp):
            conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
            c = conn.cursor()
            c.execute("UPDATE player SET experience=%s WHERE user_id=%s", (next_exp, user_id,))
            conn.commit()

    class item:
        def get_list(user_id):
            conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
            c = conn.cursor()
            c.execute("SELECT item_id, count FROM item WHERE user_id=%s ORDER BY item_id",(user_id,))
            return c.fetchall()

        def get_cnt(user_id, item_id):
            conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
            c = conn.cursor()
            c.execute("SELECT count FROM item WHERE user_id=%s and item_id=%s", (user_id, item_id))
            cnt = c.fetchone()
            return cnt[0] if cnt else 0

        def update_cnt(user_id, item_id, cnt):
            conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
            c = conn.cursor()
            if cnt <= 0:
                c.execute("DELETE FROM item WHERE user_id=%s and item_id=%s", (user_id, item_id))
            else:
                c.execute("INSERT INTO item VALUES(%s, %s, %s) ON CONFLICT(item_id,user_id) DO UPDATE SET count=%s", (item_id, user_id, cnt, cnt))
            conn.commit()

    class hp:
        def get(user_id, channel_id=None):
            conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
            c = conn.cursor()
            if channel_id:
                c.execute("SELECT player_hp FROM in_battle WHERE channel_id=%s and user_id=%s", (channel_id, user_id,))
            else:
                c.execute("SELECT channel_id, player_hp FROM in_battle WHERE user_id=%s", (user_id,))
            return c.fetchone()

        def set(user_id, channel_id, player_hp):
            conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
            c = conn.cursor()
            c.execute("INSERT INTO in_battle values(%s,%s,%s,0)", (user_id, channel_id, player_hp))
            conn.commit()

        @staticmethod
        def update(player_hp, user_id):
            conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
            c = conn.cursor()
            c.execute("UPDATE in_battle SET player_hp=%s WHERE user_id=%s", (player_hp, user_id,))
            conn.commit()


class boss_status:
    def get(channel_id):
        conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
        c = conn.cursor()
        c.execute("SELECT boss_level, boss_hp, boss_id FROM channel_status WHERE channel_id=%s", (channel_id,))
        return c.fetchone()

    def set(channel_id, boss_id, boss_level, boss_hp):
        conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
        c = conn.cursor()
        c.execute("INSERT INTO channel_status values( %s, %s, %s, %s)", (channel_id, boss_id, boss_level, boss_hp))
        conn.commit()

    def update(boss_hp, channel_id):
        conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
        c = conn.cursor()
        c.execute("UPDATE channel_status SET boss_hp=%s WHERE channel_id=%s", (boss_hp, channel_id,))
        conn.commit()


class channel:
    def all_player(channel_id):
        conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
        c = conn.cursor()
        c.execute("SELECT * FROM in_battle WHERE channel_id=%s", (channel_id,))
        return c.fetchall()

    def end_battle(channel_id):
        conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
        c = conn.cursor()
        c.execute("DELETE FROM in_battle WHERE channel_id=%s", (channel_id,))
        conn.commit()

    def enemy_levelup(channel_id, boss_id, level_up=False):
        conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
        c = conn.cursor()
        query = "UPDATE channel_status SET {} WHERE channel_id=%s".format(
            "boss_level=boss_level+1, boss_hp=boss_level*10+60" if level_up else "boss_hp=boss_level*10+50"
        )
        c.execute(query, (channel_id,))
        conn.commit()

    def set_boss_id(channel_id, boss_id):
        conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
        c = conn.cursor()
        c.execute("UPDATE channel_status SET boss_id=%s WHERE channel_id=%s", (boss_id, channel_id))


    def all_battle_player(channel_id):
        conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
        c = conn.cursor()
        c.execute("SELECT player.user_id, player.experience FROM in_battle, player WHERE in_battle.channel_id=%s AND player.user_id=in_battle.user_id",(channel_id,))
        return c.fetchall()

    def not_found(b_ch, a_ch, user_id, player_hp):
        conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
        c = conn.cursor()
        c.execute("DELETE FROM in_battle WHERE channel_id=%s", (b_ch,))
        c.execute("INSERT INTO in_battle values(%s,%s,%s,0)", (a_ch, user_id, player_hp))

    def is_battle(channel_id):
        conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
        c = conn.cursor()
        c.execute("SELECT 0 FROM in_battle WHERE channel_id=%s", (channel_id,))
        return c.fetchone()


class shop:
    class rate:
        def all():
            conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
            c = conn.cursor()
            c.execute("SELECT * FROM shop_trade")
            return c.fetchall()

        def select(item_id):
            conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
            c = conn.cursor()
            c.execute("SELECT * FROM shop_trade WHERE item_id=%s", (item_id,))
            return c.fetchone()

    def sell(user_id, s_id, s_cnt, money):
        conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
        c = conn.cursor()
        c.execute("UPDATE item SET count=count-%s WHERE user_id=%s and item_id=%s", (s_cnt, user_id, s_id))
        c.execute("UPDATE player SET money=%s WHERE user_id=%s", (money, user_id))

    def buy(user_id, s_id, s_cnt):
        pass


class account:
    def save(user_id, sha512, msg_id):
        conn = psycopg2.connect(os.environ.get('DATABASE_URL_ffm'))
        c = conn.cursor()
        c.execute("REPLACE INTO account values(%s,%s,%s)", (user_id, sha512, msg_id))
        conn.commit()

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
        c.execute("INSERT INTO prefix VALUES(%s, %s)", (self.guild.id, prefix_str))
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
        return ans[0] if ans else ans

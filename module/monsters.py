import requests
import random
from module import db

r = requests.get(f'{db.CONFIG_ROOT}/Discord/FFM/assets/monsters.json')
monsters = r.json()


def init():
    global monsters
    if all(i.isdecimal() for i in monsters.keys()):
        return
    for m_key in monsters["monsters"].keys():
        for i, v in enumerate(monsters["monsters"][m_key]):
            monster = monsters["default"].copy()
            monster.update(v)
            monsters["monsters"][m_key][i] = monster
    monsters = monsters["monsters"]


def get(boss_lv=1, boss_id=None):
    monster_division = monsters[str(max(i for i in map(int, monsters.keys()) if boss_lv % i == 0))]
    if boss_id is None:
        monster = random.choices(list(enumerate(monster_division)),
                                 weights=[i["encounter rate"] for i in monster_division])[0]
    else:
        monster = (boss_id, monster_division[boss_id])
    return monster


init()

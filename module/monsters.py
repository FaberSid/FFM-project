import requests
import random
from module import db

r = requests.get(f'{db.CONFIG_ROOT}/Discord/FFM/assets/monsters.json')
monsters = r.json()


def init():
    global monsters
    if all((i in monsters.keys()) for i in ["default", "monsters"]):
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
        monster = random.choice(list(enumerate(monster_division)))
    else:
        monster = (boss_id, monster_division[boss_id])
    return monster


init()

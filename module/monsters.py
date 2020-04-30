import requests
import random
from module import db
import copy

with open('../assets/monsters.json', encoding='utf-8') as f:
    monsters = json.load(f)


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
        try:
            monster = (boss_id, monster_division[boss_id])
        except:
            print("ERROR boss_id: ",boss_id)
            return None
    return copy.deepcopy(monster)


init()

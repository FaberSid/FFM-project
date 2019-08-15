import requests
import random
from module import db

r = requests.get(f'{db.CONFIG_ROOT}/Discord/FFM/assets/monsters.json')
monsters = r.json()


def get(boss_lv=1, boss_id=None):
    Lv_division = list(map(int, monsters["monsters"].keys()))
    monster_division = monsters["monsters"][str(max([i for i in Lv_division if i <= (boss_lv - 1) % max(Lv_division) + 1]))]
    monster = monsters["default"].copy()
    if boss_id is None:
        monster_details = random.choice(list(enumerate(monster_division[1:], 1)))
    else:
        monster_details = (boss_id, monster_division[boss_id])
    monster.update(monster_details[1])
    return monster_details[0], monster

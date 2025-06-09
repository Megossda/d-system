# File: enemies/cr_0_quarter/goblin.py
from ..base_enemy import Enemy
from equipment.weapons.martial_melee import scimitar
from equipment.armor.light import leather
from equipment.armor.shields import shield


class Goblin(Enemy):
    """A standard Goblin enemy."""

    def __init__(self, name="Goblin", position=0):
        super().__init__(
            name=name,
            level=1,
            hp=7,
            stats={'str': 8, 'dex': 14, 'con': 10, 'int': 10, 'wis': 8, 'cha': 8},
            weapon=scimitar,
            armor=leather,
            shield=shield,
            cr='1/4',
            position=position
        )
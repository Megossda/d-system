# File: enemies/cr_half_1/hobgoblin_warrior.py
from ..base_enemy import Enemy
from equipment.weapons.base_weapon import Weapon
from equipment.armor.heavy import chain_mail
from equipment.armor.shields import shield
from ai.enemy_ai.humanoid_ai import HobgoblinWarriorAI


class HobgoblinWarrior(Enemy):
    """A more formidable Hobgoblin enemy, based on the 2024 stat block."""

    def __init__(self, name="Hobgoblin Warrior", position=0):
        # Custom weapons for this enemy
        hobgoblin_longsword = Weapon(
            name="Hobgoblin Longsword",
            damage_dice="2d10",
            damage_type="Slashing"
        )
        hobgoblin_longbow = Weapon(
            name="Poisoned Longbow",
            damage_dice="1d8",
            damage_type="Piercing",
            properties=['Ranged', 'Extra Damage:3d4 Poison']
        )

        super().__init__(
            name=name,
            level=3,
            hp=11,
            stats={'str': 13, 'dex': 12, 'con': 12, 'int': 10, 'wis': 10, 'cha': 9},
            weapon=hobgoblin_longsword,
            armor=chain_mail,
            shield=shield,
            cr='1/2',
            position=position,
            initiative_bonus=2
        )
        self.secondary_weapon = hobgoblin_longbow
        self.ai_brain = HobgoblinWarriorAI()

    def attack(self, target, action_type="ACTION", weapon=None, extra_damage_dice=None):
        weapon_to_use = weapon or self.equipped_weapon
        # For now, Martial Advantage is not implemented as we only have 1v1 combat
        has_martial_advantage = False
        super().attack(target, action_type, weapon=weapon_to_use,
                       extra_damage_dice="2d6" if has_martial_advantage else None)

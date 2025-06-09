from base_character import Character
from ai_brain import AIBrain, HobgoblinWarriorAIBrain
from equipment.weapons.base_weapon import Weapon
from equipment.weapons.martial_melee import scimitar
from equipment.armor.light import leather
from equipment.armor.heavy import chain_mail
from equipment.armor.shields import shield
from core import roll


class Enemy(Character):
    """A base class for all enemy creatures."""

    def __init__(self, name, level, hp, stats, weapon, armor, shield, cr, speed=30, position=0, initiative_bonus=0):
        super().__init__(name=name, level=level, hp=hp, stats=stats,
                         weapon=weapon, armor=armor, shield=shield,
                         cr=cr, position=position, speed=speed, xp=0, initiative_bonus=initiative_bonus)
        self.ai_brain = AIBrain()


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


class HobgoblinWarrior(Enemy):
    """A more formidable Hobgoblin enemy, based on the 2024 stat block."""

    def __init__(self, name="Hobgoblin Warrior", position=0):
        # --- Corrected weapon stats based on the 2024 Monster Manual ---
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
        self.ai_brain = HobgoblinWarriorAIBrain()

    def attack(self, target, action_type="ACTION", weapon=None, extra_damage_dice=None):
        weapon_to_use = weapon or self.equipped_weapon
        # For now, Martial Advantage is not implemented as we only have 1v1 combat
        has_martial_advantage = False
        super().attack(target, action_type, weapon=weapon_to_use,
                       extra_damage_dice="2d6" if has_martial_advantage else None)


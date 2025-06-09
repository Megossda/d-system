# File: enemies/base_enemy.py
from characters.base_character import Character
from ai.base_ai import AIBrain


class Enemy(Character):
    """A base class for all enemy creatures."""

    def __init__(self, name, level, hp, stats, weapon, armor=None, shield=None,
                 cr="0", speed=30, position=0, initiative_bonus=0):
        super().__init__(name=name, level=level, hp=hp, stats=stats,
                         weapon=weapon, armor=armor, shield=shield,
                         cr=cr, position=position, speed=speed, xp=0,
                         initiative_bonus=initiative_bonus)
        self.ai_brain = AIBrain()
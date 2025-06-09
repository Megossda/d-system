# File: enemies/cr_2_5/giant_constrictor_snake.py
from ..base_enemy import Enemy
from equipment.weapons.base_weapon import Weapon
from ai.enemy_ai.beast_ai import GiantConstrictorSnakeAI
from actions.special_actions import MultiattackAction
from core import roll_d20, get_ability_modifier, roll


class GiantConstrictorSnake(Enemy):
    """A Giant Constrictor Snake - CR 2 challenge for higher level characters."""

    def __init__(self, name="Giant Constrictor Snake", position=0):
        # Natural weapons for the snake
        snake_bite = Weapon(
            name="Bite",
            damage_dice="2d6",
            damage_type="Piercing",
            properties=['Reach']  # 10ft reach
        )

        snake_constrict = Weapon(
            name="Constrict",
            damage_dice="2d8",
            damage_type="Bludgeoning",
            properties=['Grapple']  # Special grappling weapon
        )

        super().__init__(
            name=name,
            level=5,  # Rough level equivalent for CR 2
            hp=60,  # 8d12 + 8
            stats={'str': 19, 'dex': 14, 'con': 12, 'int': 1, 'wis': 10, 'cha': 3},
            weapon=snake_bite,
            armor=None,  # Natural AC
            shield=None,
            cr='2',
            position=position,
            initiative_bonus=2,
            speed=30
        )
        self.secondary_weapon = snake_constrict
        self.ai_brain = GiantConstrictorSnakeAI()
        self.size = 'Huge'
        self.is_grappling = False
        self.grapple_target = None

    def calculate_ac(self):
        """Override AC calculation for natural armor"""
        return 12  # Natural armor

    def multiattack(self, target, action_type="ACTION"):
        """Snake's multiattack: Bite + Constrict"""
        print(f"{action_type}: {self.name} uses Multiattack!")

        # First attack: Bite
        print(f"** BITE ATTACK **")
        self.attack(target, "MULTIATTACK", weapon=self.equipped_weapon)

        # Second attack: Constrict (only if target is Large or smaller)
        if target.is_alive and not self.is_grappling:
            print(f"** CONSTRICT ATTACK **")
            self.constrict_attack(target)

    def constrict_attack(self, target):
        """Special constrict attack with grappling"""
        if not self.is_alive or not target or not target.is_alive:
            return

        print(f"CONSTRICT: {self.name} attempts to constrict {target.name} (AC: {target.ac}) with Constrict!")

        attack_roll, _ = roll_d20()
        attack_modifier = get_ability_modifier(self.stats['str'])
        prof_bonus = self.get_proficiency_bonus()
        total_attack = attack_roll + attack_modifier + prof_bonus

        print(f"ATTACK ROLL: {attack_roll} (1d20) +{attack_modifier} (STR) +{prof_bonus} (Prof) = {total_attack}")

        if total_attack >= target.ac or attack_roll == 20:
            is_crit = (attack_roll == 20)
            if is_crit:
                print(">>> CRITICAL HIT! <<<")
            else:
                print("The constrict attack hits!")

            # Damage
            damage = roll(self.secondary_weapon.damage_dice)
            if is_crit:
                damage += roll(self.secondary_weapon.damage_dice)

            damage += attack_modifier
            print(f"{self.name} deals {damage} bludgeoning damage and grapples {target.name}!")
            target.take_damage(damage, attacker=self)

            # Grapple effect
            if target.is_alive:
                self.is_grappling = True
                self.grapple_target = target
                target.is_grappled = True
                print(f"** {target.name} is GRAPPLED by the snake! **")
        else:
            print("The constrict attack misses.")

    def squeeze_damage(self, target):
        """Apply ongoing squeeze damage to grappled target"""
        if self.is_grappling and self.grapple_target == target:
            squeeze_damage = roll('2d8') + get_ability_modifier(self.stats['str'])
            print(f"** {target.name} takes {squeeze_damage} bludgeoning damage from being squeezed! **")
            target.take_damage(squeeze_damage, attacker=self)

    def process_effects_on_turn_start(self):
        """Process grappling effects at start of turn"""
        super().process_effects_on_turn_start()

        if self.is_grappling and self.grapple_target and self.grapple_target.is_alive:
            print(f"** {self.name} squeezes {self.grapple_target.name}! **")
            self.squeeze_damage(self.grapple_target)
        elif self.is_grappling:
            # Target is dead, release grapple
            self.is_grappling = False
            self.grapple_target = None
# File: enemies/cr_2_5/giant_constrictor_snake.py (COMPLETE REPLACEMENT)
from ..base_enemy import Enemy
from equipment.weapons.base_weapon import Weapon
from ai.enemy_ai.beast.giant_constrictor_snake_ai import GiantConstrictorSnakeAI
from actions.special_actions import MultiattackAction
from core import roll_d20, get_ability_modifier, roll


class GiantConstrictorSnake(Enemy):
    """A Giant Constrictor Snake - CR 2 challenge with proper multiattack."""

    def __init__(self, name="Giant Constrictor Snake", position=0):
        # Natural weapons for the snake
        snake_bite = Weapon(
            name="Bite",
            damage_dice="2d6",
            damage_type="Piercing",
            properties=['Reach'],  # 10ft reach
            reach=10
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
            initiative_bonus=0,  # FIXED: DEX +2 gives total +2, no racial bonus
            speed=30
        )
        self.secondary_weapon = snake_constrict
        self.ai_brain = GiantConstrictorSnakeAI()
        self.size = 'Huge'
        self.is_grappling = False
        self.grapple_target = None

        # IMPORTANT: Add MultiattackAction to available actions
        self.available_actions.append(MultiattackAction(self))

    def calculate_ac(self):
        """Override AC calculation for natural armor"""
        return 12  # Natural armor from stat block

    def multiattack(self, target, action_type="ACTION"):
        """Snake's multiattack: Bite + Constrict (if not already grappling someone)"""
        print(f"{action_type}: {self.name} uses Multiattack!")
        print(f"** Making a Bite attack and a Constrict attack **")

        # First attack: Bite (with reach)
        print(f"\n--- BITE ATTACK (Reach 10ft) ---")
        self.bite_attack(target)

        # Second attack: Constrict (only if not already grappling and target is in range)
        if target.is_alive and abs(self.position - target.position) <= 5:
            if not self.is_grappling:
                print(f"\n--- CONSTRICT ATTACK ---")
                self.constrict_attack(target)
            else:
                print(f"\n--- Already grappling {self.grapple_target.name}, cannot constrict another target ---")
        else:
            print(f"\n--- Target too far for Constrict attack (needs 5ft range) ---")

    def bite_attack(self, target):
        """Bite attack with 10ft reach"""
        if not self.is_alive or not target or not target.is_alive:
            return

        # Check range (Bite has 10ft reach)
        distance = abs(self.position - target.position)
        if distance > 10:
            print(
                f"BITE: {self.name} tries to bite {target.name}, but is out of range (distance: {distance}ft, reach: 10ft)")
            return

        print(f"BITE: {self.name} attacks {target.name} (AC: {target.ac}) with Bite!")

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
                print("The bite attack hits!")

            # Damage calculation
            damage = roll(self.equipped_weapon.damage_dice)
            if is_crit:
                crit_damage = roll(self.equipped_weapon.damage_dice)
                damage += crit_damage
                print(f"CRIT DAMAGE: Doubled dice from {self.equipped_weapon.damage_dice}")

            total_damage = damage + attack_modifier
            print(
                f"{self.name} deals {total_damage} piercing damage ({damage} [{self.equipped_weapon.damage_dice}{'+ crit' if is_crit else ''}] +{attack_modifier} [STR])")
            target.take_damage(total_damage, attacker=self)
        else:
            print("The bite attack misses.")

    def constrict_attack(self, target):
        """Constrict attack with grappling (5ft range only)"""
        if not self.is_alive or not target or not target.is_alive:
            return

        # Check range (Constrict is melee, 5ft only)
        distance = abs(self.position - target.position)
        if distance > 5:
            print(
                f"CONSTRICT: {self.name} tries to constrict {target.name}, but is out of range (distance: {distance}ft, reach: 5ft)")
            return

        print(f"CONSTRICT: {self.name} attempts to constrict {target.name} (AC: {target.ac})!")

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

            # Damage calculation
            damage = roll(self.secondary_weapon.damage_dice)
            if is_crit:
                crit_damage = roll(self.secondary_weapon.damage_dice)
                damage += crit_damage
                print(f"CRIT DAMAGE: Doubled dice from {self.secondary_weapon.damage_dice}")

            total_damage = damage + attack_modifier
            print(
                f"{self.name} deals {total_damage} bludgeoning damage ({damage} [{self.secondary_weapon.damage_dice}{'+ crit' if is_crit else ''}] +{attack_modifier} [STR])")
            target.take_damage(total_damage, attacker=self)

            # Apply grapple effect (target must be Large or smaller)
            if target.is_alive:
                self.is_grappling = True
                self.grapple_target = target
                target.is_grappled = True
                print(f"** {target.name} is GRAPPLED by the snake! **")
                print(f"** {target.name} has the Grappled condition and cannot move! **")

                # Automatic restraint damage at start of grappler's turn
                print(f"** While grappled, {target.name} will take automatic crush damage each round! **")
        else:
            print("The constrict attack misses.")

    def process_effects_on_turn_start(self):
        """Process grappling effects and ongoing spell effects at start of turn"""
        super().process_effects_on_turn_start()

        # Process Searing Smite ongoing damage
        if hasattr(self, 'searing_smite_effect') and self.searing_smite_effect.get('active', False):
            effect = self.searing_smite_effect
            dice_count = effect['dice_count']
            save_dc = effect['save_dc']
            caster = effect['caster']
            
            # Deal ongoing fire damage
            ongoing_damage = 0
            for _ in range(dice_count):
                ongoing_damage += roll('1d6')
            
            print(f"** {self.name} takes {ongoing_damage} fire damage ({dice_count}d6) from Searing Smite! **")
            self.take_damage(ongoing_damage, attacker=caster)
            
            # Constitution saving throw to end the effect
            if self.is_alive:
                print(f"** {self.name} makes a Constitution saving throw to extinguish the flames **")
                if self.make_saving_throw('con', save_dc):
                    print(f"** {self.name} succeeds and extinguishes the searing flames! **")
                    self.searing_smite_effect['active'] = False
                    del self.searing_smite_effect
                else:
                    print(f"** {self.name} fails and continues burning! **")

        # Apply automatic crush damage to grappled target
        if self.is_grappling and self.grapple_target and self.grapple_target.is_alive:
            print(f"** AUTOMATIC CRUSH: {self.name} crushes {self.grapple_target.name}! **")
            crush_damage = roll('2d8') + get_ability_modifier(self.stats['str'])
            print(f"** {self.grapple_target.name} takes {crush_damage} bludgeoning damage from being crushed! **")
            self.grapple_target.take_damage(crush_damage, attacker=self)
        elif self.is_grappling and (not self.grapple_target or not self.grapple_target.is_alive):
            # Target is dead or missing, release grapple
            print(f"** {self.name} releases its grapple **")
            self.is_grappling = False
            self.grapple_target = None

    def take_damage(self, damage, attacker=None):
        """Override to handle grapple breaking on death"""
        super().take_damage(damage, attacker)

        # If the snake dies, release any grappled targets
        if not self.is_alive and self.is_grappling and self.grapple_target:
            print(f"** {self.grapple_target.name} is freed from the grapple! **")
            self.grapple_target.is_grappled = False
            self.is_grappling = False
            self.grapple_target = None
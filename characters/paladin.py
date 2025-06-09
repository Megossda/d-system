from core import roll_d20, roll, get_ability_modifier
from .base_character import Character  # FIXED
from spells.level_1.level_1 import searing_smite, cure_wounds, guiding_bolt
from effects import SearingSmiteEffect
from actions import CastSpellAction, LayOnHandsAction
from ai.character_ai.paladin_ai import PaladinAIBrain  # FIXED


class Paladin(Character):
    """A Paladin class with spellcasting and advanced healing abilities."""

    def __init__(self, name, level, hp, stats, weapon, armor=None, shield=None, oath=None, position=0, xp=0):
        save_proficiencies = ['Wisdom', 'Charisma']
        skill_proficiencies = ['Athletics', 'Persuasion']
        weapon_proficiencies = ['Simple', 'Martial']

        super().__init__(name=name, level=level, hp=hp, stats=stats,
                         weapon=weapon, armor=armor, shield=shield,
                         skill_proficiencies=skill_proficiencies,
                         save_proficiencies=save_proficiencies,
                         weapon_proficiencies=weapon_proficiencies,
                         position=position, xp=xp)

        self.spell_slots = {1: self.get_spell_slots_for_level(1)}
        self.prepared_spells = []
        self.active_smites = []
        self.oath = oath
        self.oath_spells = []

        self.spellcasting_ability_name = "CHA"
        self.ai_brain = PaladinAIBrain()

        # Level 1 Features
        self.lay_on_hands_pool = level * 5
        self.available_bonus_actions.append(LayOnHandsAction())

        if self.oath:
            self.oath_spells = self.oath.get_oath_spells(self.level)
            if guiding_bolt in self.oath_spells:
                self.available_actions.append(CastSpellAction(guiding_bolt))

        self.available_bonus_actions.append(CastSpellAction(searing_smite))

    def prepare_spells(self, spells_to_prepare):
        """Prepare spells and add them to available actions"""
        self.prepared_spells = list(set(spells_to_prepare + self.oath_spells))
        print(f"{self.name} has prepared the following spells: {[s.name for s in self.prepared_spells]}")

        # Add prepared spells to available actions
        if cure_wounds in self.prepared_spells:
            # Remove any existing Cure Wounds action first
            self.available_actions = [a for a in self.available_actions if a.name != "Cast Cure Wounds"]
            self.available_actions.append(CastSpellAction(cure_wounds))

    def use_lay_on_hands(self, amount, target):
        """Enhanced Lay on Hands with smarter healing amounts."""
        if self.lay_on_hands_pool <= 0:
            print(f"{self.name} tries to use Lay on Hands, but the pool is empty!")
            return

        # Smart healing: heal exactly what's needed or use a reasonable amount
        hp_needed = target.max_hp - target.hp
        heal_amount = min(amount, self.lay_on_hands_pool, hp_needed)

        # Minimum viable healing
        if heal_amount <= 0:
            print(f"BONUS ACTION: {self.name} uses Lay on Hands, but {target.name} is already at full health.")
            return

        self.lay_on_hands_pool -= heal_amount
        target.hp += heal_amount

        print(f"BONUS ACTION: {self.name} uses Lay on Hands on {target.name}, healing for {heal_amount} HP.")
        print(f"{target.name}'s HP is now {target.hp}/{target.max_hp}. ({self.lay_on_hands_pool} HP remaining in pool)")

    def get_optimal_lay_on_hands_amount(self, target):
        """Calculate optimal Lay on Hands healing amount"""
        hp_needed = target.max_hp - target.hp

        if hp_needed <= 0:
            return 0
        elif hp_needed <= 5:
            return hp_needed  # Heal exactly what's needed
        elif self.lay_on_hands_pool >= 10:
            return min(10, hp_needed)  # Standard 10 HP heal
        else:
            return min(self.lay_on_hands_pool, hp_needed)  # Use remaining pool

    def get_spell_slots_for_level(self, spell_level):
        if self.level < 2: return 0
        if spell_level == 1:
            if self.level < 3: return 2
            if self.level < 5: return 3
            return 4
        return 0

    def get_spellcasting_modifier(self):
        return get_ability_modifier(self.stats['cha'])

    def get_spell_save_dc(self):
        return 8 + self.get_proficiency_bonus() + self.get_spellcasting_modifier()

    def cast_spell(self, spell, target=None, action_type="ACTION"):
        if spell not in self.prepared_spells:
            return False
        return spell.cast(self, target)

    def attack(self, target, action_type="ACTION", weapon=None, extra_damage_dice=None):
        """Paladin's attack, with detailed logging and FIXED critical hits."""
        if not self.is_alive or not target or not target.is_alive: return

        weapon_to_use = weapon or self.equipped_weapon

        if abs(self.position - target.position) > 5:
            print(
                f"{action_type}: {self.name} tries to attack {target.name} with {weapon_to_use.name}, but is out of range.")
            return

        print(f"{action_type}: {self.name} attacks {target.name} (AC: {target.ac}) with {weapon_to_use.name}!")

        if target.grants_advantage_to_next_attacker:
            self.has_advantage = True
            target.grants_advantage_to_next_attacker = False

        attack_roll, _ = roll_d20(advantage=self.has_advantage, disadvantage=self.has_disadvantage)
        advantage_text = ""
        if self.has_advantage and not self.has_disadvantage:
            advantage_text = " (with advantage)"
        elif self.has_disadvantage and not self.has_advantage:
            advantage_text = " (with disadvantage)"
        self.has_advantage = False
        self.has_disadvantage = False

        attack_modifier = self.get_attack_modifier()
        prof_bonus = self.get_proficiency_bonus()
        total_attack = attack_roll + attack_modifier + prof_bonus
        print(
            f"ATTACK ROLL: {attack_roll} (1d20{advantage_text}) +{attack_modifier} (STR) +{prof_bonus} (Prof) = {total_attack}")

        if total_attack >= target.ac or attack_roll == 20:
            is_crit = (attack_roll == 20)
            if is_crit:
                print(">>> CRITICAL HIT! <<<")
            else:
                print("The attack hits!")

            damage_parts = {}

            # FIXED: Proper critical hit damage calculation
            weapon_damage = roll(weapon_to_use.damage_dice)
            crit_label = weapon_to_use.damage_dice

            # Check for magic weapon bonus
            magic_bonus = 0
            if '+1' in weapon_to_use.name:
                magic_bonus = 1
            elif '+2' in weapon_to_use.name:
                magic_bonus = 2
            elif '+3' in weapon_to_use.name:
                magic_bonus = 3

            if is_crit:
                weapon_damage += roll(weapon_to_use.damage_dice)
                # Update label to show doubled dice
                num_dice, die_type = weapon_to_use.damage_dice.split('d')
                doubled_dice = str(int(num_dice) * 2) + 'd' + die_type
                crit_label = doubled_dice

            if magic_bonus > 0:
                damage_parts[f'{weapon_damage} [{crit_label}] +{magic_bonus} [magic]'] = weapon_damage + magic_bonus
            else:
                damage_parts[f'{weapon_to_use.name} ({crit_label})'] = weapon_damage

            if extra_damage_dice:
                extra_damage = roll(extra_damage_dice)
                extra_label = extra_damage_dice
                if is_crit:
                    extra_damage += roll(extra_damage_dice)
                    # Update label for crit
                    num_dice, die_type = extra_damage_dice.split('d')
                    doubled_dice = str(int(num_dice) * 2) + 'd' + die_type
                    extra_label = doubled_dice
                damage_parts[f'Bonus ({extra_label})'] = extra_damage

            if searing_smite in self.active_smites:
                searing_dice = '1d6'
                searing_damage = roll(searing_dice)
                searing_label = searing_dice
                if is_crit:
                    searing_damage += roll(searing_dice)
                    searing_label = '2d6'
                damage_parts[f'Searing Smite ({searing_label})'] = searing_damage
                print(f"** The attack is imbued with Searing Smite! **")
                target.active_effects.append(SearingSmiteEffect(self))
                self.active_smites.remove(searing_smite)
                if self.concentrating_on == searing_smite:
                    self.concentrating_on = None

            if self.spell_slots.get(1, 0) > 0:
                self.spell_slots[1] -= 1
                divine_dice = '2d8'
                divine_damage = roll(divine_dice)
                divine_label = divine_dice
                if is_crit:
                    divine_damage += roll(divine_dice)
                    divine_label = '4d8'
                damage_parts[f'Divine Smite ({divine_label})'] = divine_damage
                print(
                    f"** {self.name} uses a level 1 spell slot for DIVINE SMITE! ({self.spell_slots[1]} remaining) **")

            total_damage = sum(damage_parts.values()) + self.get_damage_modifier()

            # Build damage log - exclude magic bonus from ability modifier addition
            damage_log_parts = []
            total_without_ability = 0
            for desc, dmg in damage_parts.items():
                if '[magic]' in desc:
                    # This already includes the magic bonus
                    damage_log_parts.append(desc)
                    total_without_ability += dmg
                else:
                    damage_log_parts.append(f"{dmg} [{desc}]")
                    total_without_ability += dmg

            damage_log = " + ".join(damage_log_parts)
            damage_log += f" +{self.get_damage_modifier()} [STR]"

            print(f"{self.name} deals a total of {total_damage} damage. ({damage_log})")
            target.take_damage(total_damage, attacker=self)
        else:
            print("The attack misses.")
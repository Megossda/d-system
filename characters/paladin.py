# File: characters/paladin.py
from core import roll_d20, roll, get_ability_modifier
from .base_character import Character
from spells.level_1.searing_smite import searing_smite
from spells.level_1.cure_wounds import cure_wounds
from spells.level_1.guiding_bolt import guiding_bolt
from effects import SearingSmiteEffect
from actions import CastSpellAction, LayOnHandsAction
from actions.special_actions import EscapeGrappleAction
from ai.character_ai.paladin_ai import PaladinAIBrain
from systems.paladin.channel_divinity import PaladinChannelDivinityMixin


class Paladin(Character, PaladinChannelDivinityMixin):
    """A Paladin class with spellcasting, advanced healing abilities, and Channel Divinity."""

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

        # Initialize Channel Divinity (level 3+ feature)
        if self.level >= 3:
            self.init_channel_divinity()

        # PHB 2024 spell slot progression
        self.spell_slots = self.get_spell_slots_by_level()
        self.prepared_spells = []
        self.active_smites = []
        self.oath = oath
        self.oath_spells = []

        self.spellcasting_ability_name = "CHA"
        self.ai_brain = PaladinAIBrain()

        # Level 1 Features
        self.lay_on_hands_pool = level * 5
        self.available_bonus_actions.append(LayOnHandsAction())
        
        # FIXED: Add Escape Grapple action to available actions
        self.available_actions.append(EscapeGrappleAction())

        if self.oath:
            self.oath_spells = self.oath.get_oath_spells(self.level)
            if guiding_bolt in self.oath_spells:
                self.available_actions.append(CastSpellAction(guiding_bolt))

        self.available_bonus_actions.append(CastSpellAction(searing_smite))

        # Initialize oath-specific features (level 3+)
        if self.level >= 3:
            self.initialize_oath_features()

    def get_spell_slots_by_level(self):
        """Get spell slots based on PHB 2024 Paladin table."""
        # Level 1 has 2 first-level slots, starts spellcasting immediately
        spell_slot_table = {
            1: {1: 2},
            2: {1: 2},
            3: {1: 3},
            4: {1: 3},
            5: {1: 4, 2: 2},
            6: {1: 4, 2: 2},
            7: {1: 4, 2: 3},
            8: {1: 4, 2: 3},
            9: {1: 4, 2: 3, 3: 2},
            10: {1: 4, 2: 3, 3: 2},
            11: {1: 4, 2: 3, 3: 3},
            12: {1: 4, 2: 3, 3: 3},
            13: {1: 4, 2: 3, 3: 3, 4: 1},
            14: {1: 4, 2: 3, 3: 3, 4: 1},
            15: {1: 4, 2: 3, 3: 3, 4: 2},
            16: {1: 4, 2: 3, 3: 3, 4: 2},
            17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
            18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
            19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
            20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2}
        }

        return spell_slot_table.get(self.level, {})

    def get_spell_slots_for_level(self, spell_level):
        """Legacy method for backwards compatibility."""
        return self.spell_slots.get(spell_level, 0)

    def prepare_spells(self, spells_to_prepare):
        """Prepare spells and add them to available actions - PHB 2024 version"""

        # Import divine_smite
        from spells.level_1.divine_smite import divine_smite

        # PHB 2024: Divine Smite is always prepared (like a class feature)
        always_prepared = [divine_smite]

        # Add oath spells (these are also always prepared)
        if self.oath_spells:
            always_prepared.extend(self.oath_spells)

        # Combine always prepared + chosen spells
        self.prepared_spells = list(set(always_prepared + spells_to_prepare))

        print(f"{self.name} has prepared the following spells:")
        print(f"  Always Prepared: {[s.name for s in always_prepared]}")
        print(f"  Chosen Spells: {[s.name for s in spells_to_prepare]}")
        print(f"  Total: {[s.name for s in self.prepared_spells]}")

        # Add prepared spells to available actions (only action spells, not smites)
        if cure_wounds in self.prepared_spells:
            # Remove any existing Cure Wounds action first
            self.available_actions = [a for a in self.available_actions if a.name != "Cast Cure Wounds"]
            self.available_actions.append(CastSpellAction(cure_wounds))

    def initialize_oath_features(self):
        """Initialize oath-specific features (call this in __init__ after oath setup)."""
        if self.oath and self.level >= 3:
            # Add oath-specific Channel Divinity options
            oath_cd_options = self.oath.get_channel_divinity_options(self.level)
            for option in oath_cd_options:
                self.add_channel_divinity_option(option)

            # Apply oath-specific auras and features
            if hasattr(self.oath, 'apply_aura_of_alacrity'):
                self.oath.apply_aura_of_alacrity(self, [])  # Empty allies list for now

    def use_inspiring_smite(self, targets=None):
        """Use Inspiring Smite after casting Divine Smite."""
        if not targets:
            targets = [self]  # Default to self
        return self.use_channel_divinity("Inspiring Smite", targets)

    def use_peerless_athlete(self):
        """Use Peerless Athlete for enhanced athleticism."""
        return self.use_channel_divinity("Peerless Athlete")

    def cast_divine_smite_with_inspiring_option(self, target, spell_level=1, is_crit=False, allies_nearby=None):
        """Cast Divine Smite with option to follow up with Inspiring Smite."""
        from spells.level_1.divine_smite import divine_smite

        # Cast Divine Smite normally
        success = divine_smite.cast(self, target, spell_level, is_crit)

        if success and self.channel_divinity_uses > 0:
            # Check if we have Inspiring Smite available
            has_inspiring_smite = any(option.name == "Inspiring Smite" for option in self.channel_divinity_options)

            if has_inspiring_smite:
                print(f"** {self.name} can use Inspiring Smite (Channel Divinity) to distribute temp HP! **")
                if allies_nearby:
                    return self.use_inspiring_smite(allies_nearby)

        return success

    def use_lay_on_hands(self, amount, target):
        """PHB 2024 Lay on Hands - enhanced healing and condition removal."""
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

        # Perform the healing
        self.lay_on_hands_pool -= heal_amount
        target.hp += heal_amount

        print(f"BONUS ACTION: {self.name} uses Lay on Hands on {target.name}, healing for {heal_amount} HP.")
        print(f"{target.name}'s HP is now {target.hp}/{target.max_hp}. ({self.lay_on_hands_pool} HP remaining in pool)")

        # PHB 2024: Can also remove Poisoned condition
        if hasattr(target, 'is_poisoned') and target.is_poisoned:
            if self.lay_on_hands_pool >= 5:
                print(
                    f"** {self.name} also removes the Poisoned condition from {target.name} (costs 5 HP from pool) **")
                self.lay_on_hands_pool -= 5
                target.is_poisoned = False
                print(f"({self.lay_on_hands_pool} HP remaining in pool)")

    def use_restoring_touch(self, target, conditions_to_remove):
        """Level 14 feature - enhanced Lay on Hands that removes conditions."""
        if self.level < 14:
            print(f"{self.name} doesn't have Restoring Touch yet (requires level 14)")
            return False

        if self.lay_on_hands_pool <= 0:
            print(f"{self.name} tries to use Restoring Touch, but the Lay on Hands pool is empty!")
            return False

        # PHB 2024 Restoring Touch conditions
        removable_conditions = ['Blinded', 'Charmed', 'Deafened', 'Frightened', 'Paralyzed', 'Stunned']
        total_cost = 0
        removed_conditions = []

        for condition in conditions_to_remove:
            if condition in removable_conditions:
                if hasattr(target, f'is_{condition.lower()}') and getattr(target, f'is_{condition.lower()}'):
                    if self.lay_on_hands_pool >= (total_cost + 5):
                        total_cost += 5
                        removed_conditions.append(condition)
                        setattr(target, f'is_{condition.lower()}', False)
                    else:
                        print(
                            f"Not enough Lay on Hands points to remove {condition} (need 5, have {self.lay_on_hands_pool - total_cost})")

        if removed_conditions:
            self.lay_on_hands_pool -= total_cost
            print(f"** {self.name} uses Restoring Touch to remove conditions: {', '.join(removed_conditions)} **")
            print(f"** Cost: {total_cost} HP from Lay on Hands pool ({self.lay_on_hands_pool} remaining) **")
            return True
        else:
            print(f"No valid conditions to remove on {target.name}")
            return False

    def attempt_grapple_escape(self, grappler, action_type="ACTION"):
        """Attempt to escape from a grapple using Athletics or Acrobatics (PHB 2024)"""
        print(f"--- {self.name} attempts to break free from {grappler.name}'s grapple! ---")

        # Choose between Athletics (STR) or Acrobatics (DEX)
        athletics_mod = get_ability_modifier(self.stats['str'])
        acrobatics_mod = get_ability_modifier(self.stats['dex'])

        # For Paladin, Athletics is usually better (STR-based class + proficiency)
        if 'Athletics' in self.skill_proficiencies:
            athletics_mod += self.get_proficiency_bonus()
            chosen_skill = "Athletics"
            my_modifier = athletics_mod
            ability = "STR"
            prof_text = f" +{self.get_proficiency_bonus()} (Prof)"
        elif 'Acrobatics' in self.skill_proficiencies:
            acrobatics_mod += self.get_proficiency_bonus()
            chosen_skill = "Acrobatics"
            my_modifier = acrobatics_mod
            ability = "DEX"
            prof_text = f" +{self.get_proficiency_bonus()} (Prof)"
        else:
            # No proficiency, choose better raw modifier
            if athletics_mod >= acrobatics_mod:
                chosen_skill = "Athletics"
                my_modifier = athletics_mod
                ability = "STR"
            else:
                chosen_skill = "Acrobatics"
                my_modifier = acrobatics_mod
                ability = "DEX"
            prof_text = ""

        # Make the escape attempt
        escape_roll, _ = roll_d20()
        my_total = escape_roll + my_modifier

        # PHB 2024: Escape DC = 8 + grappler's STR mod + grappler's prof bonus
        grappler_str_mod = get_ability_modifier(grappler.stats['str'])
        grappler_prof = grappler.get_proficiency_bonus()
        escape_dc = 8 + grappler_str_mod + grappler_prof

        print(f"{action_type}: {self.name} ({chosen_skill}): {escape_roll} (1d20) +{my_modifier} ({ability}{prof_text}) = {my_total}")
        print(f"Escape DC: 8 +{grappler_str_mod} (STR) +{grappler_prof} (Prof) = {escape_dc}")

        if my_total >= escape_dc:
            print(f"** {self.name} breaks free from the grapple! **")
            self.is_grappled = False
            grappler.is_grappling = False
            grappler.grapple_target = None
            return True
        else:
            print(f"** {self.name} fails to break free and remains grappled! **")
            return False

    def long_rest_recovery(self):
        """Override to handle both spell slots and Lay on Hands recovery."""
        # Recover spell slots
        self.spell_slots = self.get_spell_slots_by_level()

        # Recover Lay on Hands pool
        self.lay_on_hands_pool = self.level * 5

        # Recover Channel Divinity
        if hasattr(self, 'long_rest_recovery'):
            super().long_rest_recovery()  # Call PaladinChannelDivinityMixin method

        print(f"** {self.name} completes a long rest and recovers all resources! **")
        print(f"   Spell slots: {self.spell_slots}")
        print(f"   Lay on Hands: {self.lay_on_hands_pool} HP")
        if hasattr(self, 'channel_divinity_uses'):
            print(f"   Channel Divinity: {self.channel_divinity_uses} uses")

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

    def get_spellcasting_modifier(self):
        return get_ability_modifier(self.stats['cha'])

    def get_spell_save_dc(self):
        """Override to ensure consistent spell save DC calculation."""
        return 8 + self.get_proficiency_bonus() + self.get_spellcasting_modifier()

    def cast_spell(self, spell, target=None, action_type="ACTION"):
        if spell not in self.prepared_spells:
            return False
        return spell.cast(self, target)

    def attack(self, target, action_type="ACTION", weapon=None, extra_damage_dice=None, allow_divine_smite=None):
        """Paladin's attack with PHB 2024 Divine Smite as a spell."""
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

            # Calculate weapon damage with clear crit display
            damage_breakdown_parts = []
            total_damage = 0

            # Weapon damage
            weapon_damage = roll(weapon_to_use.damage_dice)
            if is_crit:
                weapon_crit_damage = roll(weapon_to_use.damage_dice)
                weapon_damage += weapon_crit_damage
                num_dice, die_type = weapon_to_use.damage_dice.split('d')
                doubled_dice = f"{int(num_dice) * 2}d{die_type}"
                damage_breakdown_parts.append(f"{weapon_damage} [{doubled_dice} CRIT from {weapon_to_use.damage_dice}]")
            else:
                damage_breakdown_parts.append(f"{weapon_damage} [{weapon_to_use.damage_dice}]")

            total_damage += weapon_damage

            # Magic weapon bonus (not doubled on crit)
            magic_bonus = 0
            if '+1' in weapon_to_use.name:
                magic_bonus = 1
            elif '+2' in weapon_to_use.name:
                magic_bonus = 2
            elif '+3' in weapon_to_use.name:
                magic_bonus = 3

            if magic_bonus > 0:
                total_damage += magic_bonus
                damage_breakdown_parts.append(f"{magic_bonus} [Magic Bonus]")

            # Searing Smite damage
            if searing_smite in self.active_smites:
                searing_damage = roll('1d6')
                if is_crit:
                    searing_crit_damage = roll('1d6')
                    searing_damage += searing_crit_damage
                    damage_breakdown_parts.append(f"{searing_damage} [2d6 CRIT Searing Smite from 1d6]")
                else:
                    damage_breakdown_parts.append(f"{searing_damage} [1d6 Searing Smite]")

                total_damage += searing_damage
                print(f"** The attack is imbued with Searing Smite! **")
                target.active_effects.append(SearingSmiteEffect(self))
                self.active_smites.remove(searing_smite)
                if self.concentrating_on == searing_smite:
                    self.concentrating_on = None

            # FIXED: Divine Smite with conservation check
            from spells.level_1.divine_smite import divine_smite
            should_use_divine_smite = False
            
            # Check if Divine Smite is available
            if (divine_smite in self.prepared_spells and
                    any(self.spell_slots.get(level, 0) > 0 for level in range(1, 6))):
                
                # If allow_divine_smite is explicitly set, use that
                if allow_divine_smite is not None:
                    should_use_divine_smite = allow_divine_smite
                else:
                    # Otherwise, check conservation status
                    should_use_divine_smite = self._should_use_divine_smite()

            if should_use_divine_smite:
                # Find highest available spell slot (Paladins often want to maximize smite damage)
                smite_level = None
                for level in range(5, 0, -1):  # Check from 5th down to 1st
                    if self.spell_slots.get(level, 0) > 0:
                        smite_level = level
                        break

                if smite_level:
                    self.spell_slots[smite_level] -= 1
                    print(
                        f"** {self.name} casts Divine Smite using a level {smite_level} spell slot! ({self.spell_slots[smite_level]} remaining) **")

                    # PHB 2024: Base damage 2d8, +1d8 per higher level
                    base_dice = 2
                    bonus_dice = smite_level - 1
                    total_smite_dice = base_dice + bonus_dice

                    smite_damage = 0
                    for _ in range(total_smite_dice):
                        smite_damage += roll('1d8')

                    if is_crit:
                        smite_crit_damage = 0
                        for _ in range(total_smite_dice):
                            smite_crit_damage += roll('1d8')
                        smite_damage += smite_crit_damage
                        damage_breakdown_parts.append(
                            f"{smite_damage} [{total_smite_dice * 2}d8 CRIT Divine Smite from {total_smite_dice}d8]")
                    else:
                        damage_breakdown_parts.append(f"{smite_damage} [{total_smite_dice}d8 Divine Smite]")

                    total_damage += smite_damage
            elif divine_smite in self.prepared_spells:
                # Have Divine Smite but choosing not to use it
                print(f"** {self.name} restrains from using Divine Smite (conserving spell slots) **")

            # Ability modifier (not doubled on crit)
            ability_modifier = self.get_damage_modifier()
            total_damage += ability_modifier
            damage_breakdown_parts.append(f"{ability_modifier} [STR]")

            # Build final damage log
            damage_log = " + ".join(damage_breakdown_parts)
            print(f"{self.name} deals a total of {total_damage} damage. ({damage_log})")
            target.take_damage(total_damage, attacker=self)
        else:
            print("The attack misses.")

    def _should_use_divine_smite(self):
        """Check if we should use Divine Smite based on current conservation status."""
        total_slots = sum(self.spell_slots.values())
        our_hp_percent = self.hp / self.max_hp
        
        # Check if we have Cure Wounds prepared
        from spells.level_1.cure_wounds import cure_wounds
        has_cure_wounds_prepared = cure_wounds in getattr(self, 'prepared_spells', [])
        
        # Conservation rules (same as AI logic):
        # 1. If we have ≤1 spell slot and Cure Wounds prepared, DON'T smite
        # 2. If HP ≤ 60% and ≤2 slots, DON'T smite (save for healing)
        # 3. If HP ≤ 35%, DON'T smite (save for emergency healing)
        
        if total_slots <= 1 and has_cure_wounds_prepared:
            print(f"[DIVINE SMITE] Restraining: Only {total_slots} slot(s) left, need for Cure Wounds")
            return False
        elif our_hp_percent <= 0.35 and total_slots >= 1 and has_cure_wounds_prepared:
            print(f"[DIVINE SMITE] Restraining: Critical HP ({our_hp_percent:.1%}), need slot for Cure Wounds")
            return False
        elif our_hp_percent <= 0.60 and total_slots <= 2 and has_cure_wounds_prepared:
            print(f"[DIVINE SMITE] Restraining: Moderate HP ({our_hp_percent:.1%}) with only {total_slots} slots")
            return False
        else:
            return True

    def __str__(self):
        """Enhanced string representation with oath and Channel Divinity info."""
        # Get base character info
        base_info = super().__str__()

        # Add oath info
        if self.oath:
            oath_info = f"\nOath: {self.oath.name}"
            base_info += oath_info

        # Add Channel Divinity info if available
        if hasattr(self, 'channel_divinity_uses'):
            cd_info = f"\nChannel Divinity: {self.channel_divinity_uses}/{self.get_channel_divinity_uses()} uses"
            base_info += cd_info

        return base_info
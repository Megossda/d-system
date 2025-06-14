from core import roll_d20, roll, get_ability_modifier, XP_FOR_NEXT_LEVEL, XP_FROM_CR
from actions import AttackAction, DodgeAction, OpportunityAttack, CastSpellAction
from actions.unarmed_strike_actions import create_unarmed_damage_action, create_unarmed_grapple_action
from ai.base_ai import AIBrain
import math


class Character:
    """Represents a generic character or monster in the D&D simulation."""

    def __init__(self, name, level, hp, stats, weapon, armor=None, shield=None,
                 skill_proficiencies=None, save_proficiencies=None,
                 weapon_proficiencies=None, position=0, speed=30,
                 cr="0", xp=0, initiative_bonus=0):
        self.name = name
        self.level = level
        self.max_hp = hp
        self.hp = hp
        self.stats = stats

        self.equipped_weapon = weapon
        self.secondary_weapon = None
        self.equipped_armor = armor
        self.equipped_shield = shield
        self.ac = self.calculate_ac()

        self.is_alive = True
        self.position = position
        self.speed = speed

        self.skill_proficiencies = skill_proficiencies or []
        self.save_proficiencies = save_proficiencies or []
        self.weapon_proficiencies = weapon_proficiencies or []

        self.cr = cr
        self.xp = xp
        self.xp_value = XP_FROM_CR.get(str(cr), 0)
        self.xp_for_next_level = XP_FOR_NEXT_LEVEL.get(level, float('inf'))

        self.ai_brain = AIBrain()

        self.initiative_bonus = initiative_bonus
        self.has_advantage = False
        self.has_disadvantage = False
        self.initiative = 0

        self.has_used_action = False
        self.has_used_bonus_action = False
        self.has_used_reaction = False
        self.available_actions = [
            AttackAction(self.equipped_weapon), 
            DodgeAction(),
            create_unarmed_damage_action(),
            create_unarmed_grapple_action()
        ]
        self.available_bonus_actions = []
        self.available_reactions = [OpportunityAttack()]
        self.active_effects = []
        self.concentrating_on = None
        self.grants_advantage_to_next_attacker = False
        self.spellcasting_ability_name = "None"
        self.active_smites = []
        self.is_grappled = False

    def calculate_ac(self):
        ac = 10 + get_ability_modifier(self.stats['dex'])
        if self.equipped_armor:
            dex_mod = get_ability_modifier(self.stats['dex'])
            if self.equipped_armor.category == "Light":
                ac = self.equipped_armor.base_ac + dex_mod
            elif self.equipped_armor.category == "Medium":
                ac = self.equipped_armor.base_ac + min(2, dex_mod)
            elif self.equipped_armor.category == "Heavy":
                ac = self.equipped_armor.base_ac
        if self.equipped_shield:
            ac += self.equipped_shield.ac_bonus
        return ac

    def roll_initiative(self):
        roll_val, _ = roll_d20()
        dex_modifier = get_ability_modifier(self.stats['dex'])
        total_initiative = roll_val + dex_modifier + self.initiative_bonus
        self.initiative = total_initiative
        log_message = f"{self.name} rolls for initiative: {roll_val} (1d20) +{dex_modifier} (DEX)"
        if self.initiative_bonus > 0:
            log_message += f" +{self.initiative_bonus} (Bonus)"
        log_message += f" = {total_initiative}"
        print(log_message)

    def __str__(self):
        stat_blocks = []
        for stat, score in self.stats.items():
            modifier = get_ability_modifier(score)
            stat_blocks.append(f"{stat.capitalize()}: {score} ({'+' if modifier >= 0 else ''}{modifier})")
        stat_line = " | ".join(stat_blocks)

        xp_line = f"XP: {self.xp}/{self.xp_for_next_level}" if self.level < 20 else f"XP: {self.xp}"
        equipment_line = f"Equipment: {self.equipped_weapon.name}"
        if self.secondary_weapon:
            equipment_line += f", {self.secondary_weapon.name}"
        if self.equipped_armor:
            equipment_line += f", {self.equipped_armor.name}"
        if self.equipped_shield:
            equipment_line += f", {self.equipped_shield.name}"

        return (f"--- {self.name} (Lvl {self.level}) ---\n"
                f"HP: {self.hp}/{self.max_hp} | AC: {self.ac} | Speed: {self.speed}ft. | {xp_line}\n"
                f"Stats: {stat_line}\n"
                f"Proficiencies: Skills={self.skill_proficiencies}, Saves={self.save_proficiencies}\n"
                f"{equipment_line}")

    def take_turn(self, combatants):
        self.has_used_action = False
        self.has_used_bonus_action = False
        
        # FIXED: Store combatants reference for grapple system
        self.current_combatants = combatants
        
        chosen_actions = self.ai_brain.choose_actions(self, combatants)

        defender = chosen_actions.get('action_target') or next((c for c in combatants if c.is_alive and c != self), None)

        moved = False
        movement_executed = 0

        # FIXED: Grappled condition prevents movement (PHB 2024)
        if hasattr(self, 'is_grappled') and self.is_grappled:
            print("MOVEMENT: (Cannot move - Grappled condition)")
            moved = True  # Prevent normal movement logic
        else:
            # Normal movement logic
            if defender and chosen_actions.get('action'):
                action = chosen_actions.get('action')
                
                # Get movement recommendation from range manager if available
                if hasattr(self, 'ai_brain') and hasattr(self.ai_brain, 'last_tactical_recommendation'):
                    tactical_rec = self.ai_brain.last_tactical_recommendation
                    if tactical_rec and tactical_rec.get('movement_needed', 0) > 0:
                        recommended_movement = min(self.speed, tactical_rec['movement_needed'])
                        if recommended_movement > 0:
                            direction = 1 if defender.position > self.position else -1
                            self.position += recommended_movement * direction
                            movement_executed = recommended_movement
                            print(f"MOVEMENT: {self.name} moves {movement_executed} feet towards {defender.name}.")
                            moved = True

                # Fallback: Original movement logic for attacks
                if not moved and isinstance(action, AttackAction):
                    weapon = action.weapon
                    is_ranged = hasattr(weapon, 'properties') and 'Ranged' in weapon.properties
                    
                    if not is_ranged:
                        # For multiattack, we need to consider the shortest range requirement
                        if hasattr(action, 'action') and hasattr(action.action, 'creature'):
                            # This is a multiattack action, check what ranges we need
                            current_distance = abs(self.position - defender.position)
                            
                            # For snake multiattack: Bite (10ft) + Constrict (5ft)
                            # Need to be within 5ft for both to work
                            if current_distance > 5:
                                needed_movement = current_distance - 5
                                actual_movement = min(self.speed, needed_movement)
                                
                                if actual_movement > 0:
                                    direction = 1 if defender.position > self.position else -1
                                    self.position += actual_movement * direction
                                    movement_executed = actual_movement
                                    print(f"MOVEMENT: {self.name} moves {movement_executed} feet towards {defender.name} (multiattack positioning).")
                                    moved = True
                        else:
                            # Regular weapon attack movement
                            weapon_reach = getattr(weapon, 'reach', 5)
                            current_distance = abs(self.position - defender.position)
                            
                            if current_distance > weapon_reach:
                                needed_movement = current_distance - weapon_reach
                                actual_movement = min(self.speed, needed_movement)
                                
                                if actual_movement > 0:
                                    direction = 1 if defender.position > self.position else -1
                                    self.position += actual_movement * direction
                                    movement_executed = actual_movement
                                    print(f"MOVEMENT: {self.name} moves {movement_executed} feet towards {defender.name}.")
                                    moved = True

        if not moved:
            print("MOVEMENT: (None)")

        # Store movement info for tactical AI
        if hasattr(self, 'ai_brain'):
            self.ai_brain.last_movement_executed = movement_executed

        bonus_action = chosen_actions.get('bonus_action')
        if bonus_action and not self.has_used_bonus_action:
            bonus_target = chosen_actions.get('bonus_action_target')
            bonus_action.execute(self, bonus_target, "BONUS ACTION")
            self.has_used_bonus_action = True
        else:
            print("BONUS ACTION: (None)")

        action = chosen_actions.get('action')
        if action and not self.has_used_action:
            action_target = chosen_actions.get('action_target')
            action.execute(self, action_target, "ACTION")
            self.has_used_action = True
        else:
            print("ACTION: (None)")

        print("REACTION: (Not used)")

    def attack(self, target, action_type="ACTION", weapon=None, extra_damage_dice=None):
        if not self.is_alive or not target or not target.is_alive: return

        weapon_to_use = weapon or self.equipped_weapon
        is_ranged = 'Ranged' in weapon_to_use.properties

        if not is_ranged and abs(self.position - target.position) > 5:
            print(
                f"{action_type}: {self.name} tries to attack {target.name} with {weapon_to_use.name}, but is out of range.")
            return

        print(f"{action_type}: {self.name} attacks {target.name} (AC: {target.ac}) with {weapon_to_use.name}!")

        # FIXED: Apply grappled condition disadvantage (PHB 2024)
        grapple_disadvantage = False
        if hasattr(self, 'is_grappled') and self.is_grappled:
            if hasattr(self, 'grappler') and self.grappler and target != self.grappler:
                grapple_disadvantage = True
                print(f"** {self.name} has disadvantage (Grappled condition - attacking someone other than grappler) **")

        if target.grants_advantage_to_next_attacker:
            # Check if advantage has expired
            current_round = getattr(self, 'current_round', 1)
            advantage_expires = getattr(target, 'advantage_expires_round', current_round)

            if current_round <= advantage_expires:
                self.has_advantage = True
                target.grants_advantage_to_next_attacker = False  # Consume the advantage
                print(f"** {self.name} gains advantage from Guiding Bolt's effect! **")
            else:
                # Advantage has expired
                target.grants_advantage_to_next_attacker = False
                print(f"** Guiding Bolt's advantage effect has expired. **")

        # Apply grapple disadvantage if applicable
        if grapple_disadvantage:
            self.has_disadvantage = True

        attack_roll, _ = roll_d20(advantage=self.has_advantage, disadvantage=self.has_disadvantage)
        advantage_text = ""
        if self.has_advantage and not self.has_disadvantage:
            advantage_text = " (with advantage)"
        elif self.has_disadvantage and not self.has_advantage:
            advantage_text = " (with disadvantage)"
        elif self.has_advantage and self.has_disadvantage:
            advantage_text = " (advantage cancelled by disadvantage)"
        
        self.has_advantage = False
        self.has_disadvantage = False

        attack_modifier_ability = 'dex' if is_ranged or 'Finesse' in weapon_to_use.properties else 'str'
        attack_modifier = get_ability_modifier(self.stats[attack_modifier_ability])

        prof_bonus = self.get_proficiency_bonus()
        total_attack = attack_roll + attack_modifier + prof_bonus
        print(
            f"ATTACK ROLL: {attack_roll} (1d20{advantage_text}) +{attack_modifier} ({attack_modifier_ability.upper()}) +{prof_bonus} (Prof) = {total_attack}")

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

            for prop in weapon_to_use.properties:
                if "Extra Damage" in prop:
                    _, dice_and_type = prop.split(':')
                    dice, dmg_type = dice_and_type.split(' ')
                    extra_damage = roll(dice)
                    extra_label = dice
                    if is_crit:
                        extra_damage += roll(dice)
                        # Update label for crit
                        num_dice, die_type = dice.split('d')
                        doubled_dice = str(int(num_dice) * 2) + 'd' + die_type
                        extra_label = doubled_dice
                    damage_parts[f'Bonus ({extra_label} {dmg_type})'] = extra_damage

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

            total_damage = sum(damage_parts.values()) + get_ability_modifier(self.stats[attack_modifier_ability])

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
            damage_log += f" +{get_ability_modifier(self.stats[attack_modifier_ability])} ({attack_modifier_ability.upper()})"

            print(f"{self.name} deals a total of {total_damage} damage. ({damage_log})")
            target.take_damage(total_damage, attacker=self)
        else:
            print("The attack misses.")

    def make_spell_attack(self, target, spell, action_type="ACTION"):
        if not self.is_alive:
            return False, False  # (hit, is_crit)

        attack_roll, _ = roll_d20(advantage=self.has_advantage, disadvantage=self.has_disadvantage)

        # Reset advantage/disadvantage flags
        advantage_text = ""
        if self.has_advantage and not self.has_disadvantage:
            advantage_text = " (with advantage)"
        elif self.has_disadvantage and not self.has_advantage:
            advantage_text = " (with disadvantage)"
        self.has_advantage = False
        self.has_disadvantage = False

        spell_attack_modifier = self.get_spellcasting_modifier()
        prof_bonus = self.get_proficiency_bonus()
        total_attack = attack_roll + spell_attack_modifier + prof_bonus

        ability_acronym = self.spellcasting_ability_name.upper()
        print(
            f"SPELL ATTACK ROLL: {attack_roll} (1d20{advantage_text}) +{spell_attack_modifier} ({ability_acronym}) +{prof_bonus} (Prof) = {total_attack}")

        is_crit = (attack_roll == 20)
        is_hit = (total_attack >= target.ac or is_crit)

        if not is_hit:
            print("The spell misses.")

        return is_hit, is_crit  # Return both hit status and crit status

    def gain_xp(self, amount):
        if not self.is_alive: return
        print(f"** {self.name} gains {amount} XP! **")
        self.xp += amount
        self.xp_for_next_level = XP_FOR_NEXT_LEVEL.get(self.level, float('inf'))
        if self.xp >= self.xp_for_next_level:
            print(f"** {self.name} has enough experience to level up! **")

    def take_damage(self, damage, attacker=None):
        self.hp -= damage
        print(f"{self.name} takes {damage} damage and has {self.hp}/{self.max_hp} HP remaining.")

        if self.concentrating_on:
            save_dc = max(10, damage // 2)
            if not self.make_saving_throw('con', save_dc):
                print(f"{self.name}'s concentration on '{self.concentrating_on.name}' is broken!")
                if self.concentrating_on in self.active_smites:
                    self.active_smites.remove(self.concentrating_on)
                self.concentrating_on = None

        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False
            print(f"{self.name} has been defeated!")
            if attacker:
                attacker.gain_xp(self.xp_value)

    def process_effects_on_turn_start(self):
        if not self.active_effects: return
        print(f"Processing effects for {self.name}'s turn...")
        for effect in list(self.active_effects):
            effect.apply(self)
            effect.tick_down()
            if effect.duration <= 0:
                print(f"'{effect.name}' has ended on {self.name}.")
                self.active_effects.remove(effect)

    def get_proficiency_bonus(self):
        return (self.level - 1) // 4 + 2

    def make_saving_throw(self, ability, dc):
        print(f"--- {self.name} must make a DC {dc} {ability.upper()} saving throw! ---")
        roll_val, _ = roll_d20()
        modifier = get_ability_modifier(self.stats[ability])
        total = roll_val + modifier
        log = f"Save: {roll_val} (1d20) +{modifier} ({ability.upper()})"
        if ability.capitalize() in self.save_proficiencies:
            prof_bonus = self.get_proficiency_bonus()
            total += prof_bonus
            log += f" +{prof_bonus} (Proficiency)"
        log += f" = {total}"
        print(log)
        if total >= dc:
            print("Save successful!")
            return True
        print("Save failed.")
        return False

    def start_concentrating(self, spell):
        if self.concentrating_on:
            print(f"{self.name}'s concentration on '{self.concentrating_on.name}' is broken!")
        print(f"{self.name} begins concentrating on {spell.name}.")
        self.concentrating_on = spell

    def get_attack_modifier(self):
        return get_ability_modifier(self.stats['str'])

    def get_spellcasting_modifier(self):
        return 0

    def get_damage_modifier(self):
        return get_ability_modifier(self.stats['str'])

    def break_grapple_attempt(self, grappler):
        """Attempt to break free from a grapple using Athletics or Acrobatics (PHB 2024)"""
        print(f"--- {self.name} attempts to break free from {grappler.name}'s grapple! ---")

        # Choose between Athletics (STR) or Acrobatics (DEX)
        athletics_mod = get_ability_modifier(self.stats['str'])
        acrobatics_mod = get_ability_modifier(self.stats['dex'])

        # For AI, choose the better modifier
        if athletics_mod >= acrobatics_mod:
            chosen_skill = "Athletics"
            my_modifier = athletics_mod
            ability = "STR"
        else:
            chosen_skill = "Acrobatics"
            my_modifier = acrobatics_mod
            ability = "DEX"

        # Add proficiency if character has it
        if chosen_skill in self.skill_proficiencies:
            my_modifier += self.get_proficiency_bonus()
            prof_text = f" +{self.get_proficiency_bonus()} (Prof)"
        else:
            prof_text = ""

        # Make the escape attempt (NO disadvantage in PHB 2024)
        escape_roll, _ = roll_d20()
        my_total = escape_roll + my_modifier

        # PHB 2024: Escape DC = 8 + grappler's STR mod + grappler's prof bonus
        grappler_str_mod = get_ability_modifier(grappler.stats['str'])
        grappler_prof = grappler.get_proficiency_bonus()
        escape_dc = 8 + grappler_str_mod + grappler_prof

        print(f"{self.name} ({chosen_skill}): {escape_roll} (1d20) +{my_modifier} ({ability}{prof_text}) = {my_total}")
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
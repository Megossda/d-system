# File: systems/grappling/universal_grapple.py
"""
Universal grappling system based on PHB 2024 rules.
Designed to mirror our working Giant Constrictor Snake logic but in reusable form.
"""

from core import roll, get_ability_modifier


class UniversalGrappling:
    """Universal grappling system that any creature can use."""

    @staticmethod
    def attempt_grapple(attacker, target, save_dc, damage_dice, damage_type="Bludgeoning", 
                       attack_name="Grapple", range_ft=10, method="save"):
        """
        Universal grapple attempt - mirrors our working Giant Constrictor Snake logic.
        
        Args:
            attacker: The creature attempting to grapple
            target: The target creature
            save_dc: Difficulty class for the save/escape
            damage_dice: Damage dice (e.g., "2d8")
            damage_type: Type of damage
            attack_name: Name of the attack (for logging)
            range_ft: Range in feet
            method: "save" (like snake) or "attack" (like PC unarmed strike)
        
        Returns:
            bool: True if grapple successful, False otherwise
        """
        if not attacker.is_alive or not target or not target.is_alive:
            return False

        # Check range
        distance = abs(attacker.position - target.position)
        if distance > range_ft:
            print(f"{attack_name.upper()}: {attacker.name} tries to {attack_name.lower()} {target.name}, "
                  f"but is out of range (distance: {distance}ft, reach: {range_ft}ft)")
            return False

        print(f"{attack_name.upper()}: {attacker.name} attempts to {attack_name.lower()} {target.name}!")

        # Method 1: Saving throw (like Giant Constrictor Snake)
        if method == "save":
            print(f"** {target.name} must make a DC {save_dc} Strength saving throw! **")
            
            if target.make_saving_throw('str', save_dc):
                print(f"** {target.name} resists the {attack_name.lower()}! **")
                return False
            
            print(f"** {target.name} fails the saving throw! **")

        # Method 2: Attack roll (like PC unarmed strike)
        elif method == "attack":
            from core import roll_d20
            attack_roll, _ = roll_d20()
            attack_modifier = get_ability_modifier(attacker.stats['str'])
            prof_bonus = attacker.get_proficiency_bonus()
            total_attack = attack_roll + attack_modifier + prof_bonus

            print(f"ATTACK ROLL: {attack_roll} (1d20) +{attack_modifier} (STR) +{prof_bonus} (Prof) = {total_attack}")

            if total_attack < target.ac and attack_roll != 20:
                print(f"The {attack_name.lower()} attack misses.")
                return False
            
            print(f"The {attack_name.lower()} attack hits!")

        # Apply damage
        damage = roll(damage_dice)
        str_mod = get_ability_modifier(attacker.stats['str'])
        total_damage = damage + str_mod
        
        print(f"{attacker.name} deals {total_damage} {damage_type.lower()} damage "
              f"({damage} [{damage_dice}] +{str_mod} [STR])")
        target.take_damage(total_damage, attacker=attacker)

        # Apply grapple if target survives
        if target.is_alive:
            return UniversalGrappling._apply_grapple_condition(attacker, target, save_dc)
        
        return False

    @staticmethod
    def _apply_grapple_condition(grappler, target, escape_dc):
        """Apply grapple conditions to both creatures - mirrors our working system."""
        # Set grapple state on both creatures (exactly like our Giant Constrictor Snake)
        grappler.is_grappling = True
        grappler.grapple_target = target
        target.is_grappled = True
        target.grappler = grappler
        target.grapple_escape_dc = escape_dc
        
        print(f"** {target.name} is GRAPPLED by {grappler.name}! **")
        print(f"** {target.name} has the Grappled condition: Speed 0, disadvantage on attacks vs others **")
        print(f"** Escape DC: {escape_dc} (STR Athletics or DEX Acrobatics check) **")
        
        return True

    @staticmethod
    def attempt_escape(grappled_creature, action_type="ACTION"):
        """
        Universal grapple escape - mirrors our working EscapeGrappleAction logic.
        
        Args:
            grappled_creature: The creature attempting to escape
            action_type: Type of action being used
            
        Returns:
            bool: True if escape successful, False otherwise
        """
        if not hasattr(grappled_creature, 'is_grappled') or not grappled_creature.is_grappled:
            print(f"{action_type}: {grappled_creature.name} is not grappled!")
            return False

        if not hasattr(grappled_creature, 'grappler') or not grappled_creature.grappler:
            print(f"{action_type}: {grappled_creature.name} has no grappler reference!")
            return False

        grappler = grappled_creature.grappler
        
        # Verify grappler is still valid
        if not grappler.is_alive:
            print(f"{action_type}: {grappled_creature.name}'s grappler is dead, automatically freed!")
            UniversalGrappling._free_from_grapple(grappled_creature, grappler)
            return True

        if not hasattr(grappler, 'is_grappling') or not grappler.is_grappling:
            print(f"{action_type}: {grappled_creature.name}'s grappler is no longer grappling, automatically freed!")
            UniversalGrappling._free_from_grapple(grappled_creature, grappler)
            return True

        # PHB 2024 escape attempt
        return UniversalGrappling._attempt_escape_roll(grappled_creature, grappler, action_type)

    @staticmethod
    def _attempt_escape_roll(performer, grappler, action_type):
        """Make the actual escape roll - mirrors our working logic exactly."""
        print(f"--- {performer.name} attempts to break free from {grappler.name}'s grapple! ---")

        # Choose between Athletics (STR) or Acrobatics (DEX)
        athletics_mod = get_ability_modifier(performer.stats['str'])
        acrobatics_mod = get_ability_modifier(performer.stats['dex'])

        # Add proficiency if character has it
        if 'Athletics' in getattr(performer, 'skill_proficiencies', []):
            athletics_mod += performer.get_proficiency_bonus()
            athletics_has_prof = True
        else:
            athletics_has_prof = False

        if 'Acrobatics' in getattr(performer, 'skill_proficiencies', []):
            acrobatics_mod += performer.get_proficiency_bonus()
            acrobatics_has_prof = True
        else:
            acrobatics_has_prof = False

        # Choose the better option
        if athletics_mod >= acrobatics_mod:
            chosen_skill = "Athletics"
            my_modifier = athletics_mod
            ability = "STR"
            base_mod = get_ability_modifier(performer.stats['str'])
            prof_text = f" +{performer.get_proficiency_bonus()} (Prof)" if athletics_has_prof else ""
        else:
            chosen_skill = "Acrobatics"
            my_modifier = acrobatics_mod
            ability = "DEX"
            base_mod = get_ability_modifier(performer.stats['dex'])
            prof_text = f" +{performer.get_proficiency_bonus()} (Prof)" if acrobatics_has_prof else ""

        # Make the escape attempt
        from core import roll_d20
        escape_roll, _ = roll_d20()
        my_total = escape_roll + my_modifier

        # Get escape DC
        escape_dc = getattr(performer, 'grapple_escape_dc', 
                           8 + get_ability_modifier(grappler.stats['str']) + grappler.get_proficiency_bonus())

        print(f"{action_type}: {performer.name} ({chosen_skill}): {escape_roll} (1d20) +{base_mod} ({ability}){prof_text} = {my_total}")
        print(f"Escape DC: {escape_dc}")

        if my_total >= escape_dc:
            print(f"** {performer.name} breaks free from the grapple! **")
            UniversalGrappling._free_from_grapple(performer, grappler)
            return True
        else:
            print(f"** {performer.name} fails to break free and remains grappled! **")
            return False

    @staticmethod
    def _free_from_grapple(performer, grappler):
        """Free the performer from grapple and clean up state - mirrors our working logic."""
        # Clear grappled state
        performer.is_grappled = False
        if hasattr(performer, 'grappler'):
            delattr(performer, 'grappler')
        if hasattr(performer, 'grapple_escape_dc'):
            delattr(performer, 'grapple_escape_dc')

        # Clear grappling state
        if hasattr(grappler, 'is_grappling'):
            grappler.is_grappling = False
        if hasattr(grappler, 'grapple_target'):
            grappler.grapple_target = None

        # FIXED: Remove creature-specific conditions (like Restrained for octopus)
        if hasattr(performer, 'is_restrained'):
            performer.is_restrained = False
            print(f"** {performer.name} is no longer restrained **")

        # FIXED: Clean up grappler's target tracking for multi-grapplers
        if hasattr(grappler, 'grappled_targets') and performer in grappler.grappled_targets:
            grappler.grappled_targets.remove(performer)

        print(f"** {performer.name} is no longer grappled! **")

    @staticmethod
    def crush_grappled_target(crusher, action_type="ACTION", damage_dice="2d8", damage_type="Bludgeoning"):
        """
        Universal crush action for grappling creatures - mirrors our working Giant Constrictor Snake logic.
        
        Args:
            crusher: The creature doing the crushing
            action_type: Type of action
            damage_dice: Damage dice for crush
            damage_type: Type of damage
            
        Returns:
            bool: True if crush successful, False otherwise
        """
        if not hasattr(crusher, 'is_grappling') or not crusher.is_grappling:
            print(f"{action_type}: {crusher.name} is not grappling anyone!")
            return False
            
        if not hasattr(crusher, 'grapple_target') or not crusher.grapple_target or not crusher.grapple_target.is_alive:
            print(f"{action_type}: {crusher.name} has no target to crush!")
            return False
        
        target = crusher.grapple_target
        print(f"{action_type}: {crusher.name} crushes {target.name} with its coils!")
        
        # GUARANTEED DAMAGE: When crushing an already-grappled target, no save required
        damage = roll(damage_dice)
        str_mod = get_ability_modifier(crusher.stats['str'])
        total_damage = damage + str_mod
        
        print(f"{crusher.name} deals {total_damage} {damage_type.lower()} damage "
              f"({damage} [{damage_dice}] +{str_mod} [STR]) - GUARANTEED")
        target.take_damage(total_damage, attacker=crusher)
        
        print(f"** {target.name} remains grappled and can attempt to escape on their turn! **")
        return True

    @staticmethod
    def cleanup_invalid_grapples(creature):
        """Clean up any invalid grapple states - utility function."""
        if hasattr(creature, 'is_grappling') and creature.is_grappling:
            if not hasattr(creature, 'grapple_target') or not creature.grapple_target or not creature.grapple_target.is_alive:
                print(f"** {creature.name} releases its grapple (target no longer valid) **")
                creature.is_grappling = False
                creature.grapple_target = None

        if hasattr(creature, 'is_grappled') and creature.is_grappled:
            if not hasattr(creature, 'grappler') or not creature.grappler or not creature.grappler.is_alive:
                print(f"** {creature.name} is freed from grapple (grappler no longer valid) **")
                creature.is_grappled = False
                if hasattr(creature, 'grappler'):
                    delattr(creature, 'grappler')
                if hasattr(creature, 'grapple_escape_dc'):
                    delattr(creature, 'grapple_escape_dc')
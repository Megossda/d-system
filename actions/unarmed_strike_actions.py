# File: actions/unarmed_strike_actions.py
from .base_actions import Action
from core import roll_d20, get_ability_modifier


class UnarmedStrikeAction(Action):
    """PHB 2024 Compliant Unarmed Strike with three options."""

    def __init__(self, option="damage"):
        self.option = option  # "damage", "grapple", or "shove"
        super().__init__(f"Unarmed Strike ({option.title()})")

    def execute(self, performer, target, action_type="ACTION"):
        """Execute the chosen Unarmed Strike option."""
        if not target:
            print(f"{action_type}: {performer.name} has no target for Unarmed Strike!")
            return False

        # Check range (5 feet for all Unarmed Strike options)
        distance = abs(performer.position - target.position)
        if distance > 5:
            print(f"{action_type}: {performer.name} tries to use Unarmed Strike on {target.name}, but is out of range (distance: {distance}ft, reach: 5ft)")
            return False

        if self.option == "damage":
            return self._damage_option(performer, target, action_type)
        elif self.option == "grapple":
            return self._grapple_option(performer, target, action_type)
        elif self.option == "shove":
            return self._shove_option(performer, target, action_type)
        else:
            print(f"Unknown Unarmed Strike option: {self.option}")
            return False

    def _damage_option(self, performer, target, action_type):
        """PHB 2024: Damage option - make attack roll, deal 1 + STR damage."""
        print(f"{action_type}: {performer.name} attacks {target.name} with Unarmed Strike (Damage)!")

        # Make attack roll
        attack_roll, _ = roll_d20()
        str_mod = get_ability_modifier(performer.stats['str'])
        prof_bonus = performer.get_proficiency_bonus()
        total_attack = attack_roll + str_mod + prof_bonus

        print(f"ATTACK ROLL: {attack_roll} (1d20) +{str_mod} (STR) +{prof_bonus} (Prof) = {total_attack}")

        if total_attack >= target.ac or attack_roll == 20:
            is_crit = (attack_roll == 20)
            if is_crit:
                print(">>> CRITICAL HIT! <<<")
            else:
                print("The unarmed strike hits!")

            # PHB 2024: Damage = 1 + STR modifier (no dice roll)
            damage = 1 + str_mod
            if is_crit:
                # Critical hits don't affect flat damage, but let's double the base 1
                damage += 1
                print(f"CRIT DAMAGE: +1 additional damage")

            print(f"{performer.name} deals {damage} bludgeoning damage (1 base +{str_mod} [STR])")
            target.take_damage(damage, attacker=performer)
            return True
        else:
            print("The unarmed strike misses.")
            return False

    def _grapple_option(self, performer, target, action_type):
        """PHB 2024: Grapple option - target makes STR/DEX save, NO damage."""
        # Check size restriction (target no more than one size larger)
        performer_size = getattr(performer, 'size', 'Medium')
        target_size = getattr(target, 'size', 'Medium')
        
        size_order = ['Tiny', 'Small', 'Medium', 'Large', 'Huge', 'Gargantuan']
        performer_size_idx = size_order.index(performer_size) if performer_size in size_order else 2
        target_size_idx = size_order.index(target_size) if target_size in size_order else 2
        
        if target_size_idx > performer_size_idx + 1:
            print(f"{action_type}: {performer.name} cannot grapple {target.name} - target is too large ({target_size} vs {performer_size})")
            return False

        # Check if performer has hand free (simplified - assume they do unless grappling)
        if hasattr(performer, 'is_grappling') and performer.is_grappling:
            print(f"{action_type}: {performer.name} has no free hand to grapple (already grappling)")
            return False

        print(f"{action_type}: {performer.name} attempts to grapple {target.name} with Unarmed Strike!")

        # PHB 2024: Target makes STR or DEX saving throw (target chooses)
        str_mod = get_ability_modifier(performer.stats['str'])
        prof_bonus = performer.get_proficiency_bonus()
        grapple_dc = 8 + str_mod + prof_bonus

        print(f"** {target.name} must make a DC {grapple_dc} Strength or Dexterity saving throw! **")
        
        # For AI/monsters, choose the better save
        target_str_mod = get_ability_modifier(target.stats.get('str', 10))
        target_dex_mod = get_ability_modifier(target.stats.get('dex', 10))
        
        if target_str_mod >= target_dex_mod:
            chosen_save = 'str'
            print(f"** {target.name} chooses Strength saving throw **")
        else:
            chosen_save = 'dex'
            print(f"** {target.name} chooses Dexterity saving throw **")

        if target.make_saving_throw(chosen_save, grapple_dc):
            print(f"** {target.name} resists the grapple attempt! **")
            return False

        print(f"** {target.name} fails the saving throw! **")

        # Apply grapple condition (PHB 2024 compliant)
        return self._apply_pc_grapple(performer, target, grapple_dc)

    def _shove_option(self, performer, target, action_type):
        """PHB 2024: Shove option - target makes STR/DEX save, push or prone."""
        # Check size restriction (target no more than one size larger)
        performer_size = getattr(performer, 'size', 'Medium')
        target_size = getattr(target, 'size', 'Medium')
        
        size_order = ['Tiny', 'Small', 'Medium', 'Large', 'Huge', 'Gargantuan']
        performer_size_idx = size_order.index(performer_size) if performer_size in size_order else 2
        target_size_idx = size_order.index(target_size) if target_size in size_order else 2
        
        if target_size_idx > performer_size_idx + 1:
            print(f"{action_type}: {performer.name} cannot shove {target.name} - target is too large ({target_size} vs {performer_size})")
            return False

        print(f"{action_type}: {performer.name} attempts to shove {target.name} with Unarmed Strike!")

        # PHB 2024: Target makes STR or DEX saving throw
        str_mod = get_ability_modifier(performer.stats['str'])
        prof_bonus = performer.get_proficiency_bonus()
        shove_dc = 8 + str_mod + prof_bonus

        print(f"** {target.name} must make a DC {shove_dc} Strength or Dexterity saving throw! **")
        
        # For AI/monsters, choose the better save
        target_str_mod = get_ability_modifier(target.stats.get('str', 10))
        target_dex_mod = get_ability_modifier(target.stats.get('dex', 10))
        
        if target_str_mod >= target_dex_mod:
            chosen_save = 'str'
            print(f"** {target.name} chooses Strength saving throw **")
        else:
            chosen_save = 'dex'
            print(f"** {target.name} chooses Dexterity saving throw **")

        if target.make_saving_throw(chosen_save, shove_dc):
            print(f"** {target.name} resists the shove attempt! **")
            return False

        print(f"** {target.name} fails the saving throw! **")

        # Choose effect: push away or knock prone (performer's choice)
        # For simplicity, always knock prone (can be enhanced later)
        target.is_prone = True
        print(f"** {target.name} is knocked prone! **")
        return True

    def _apply_pc_grapple(self, performer, target, grapple_dc):
        """Apply PHB 2024 grapple condition from PC to target."""
        # Set grapple state
        performer.is_grappling = True
        performer.grapple_target = target
        target.is_grappled = True
        target.grappler = performer
        target.grapple_escape_dc = grapple_dc
        
        print(f"** {target.name} is GRAPPLED by {performer.name}! **")
        print(f"** {target.name} has the Grappled condition: Speed 0, disadvantage on attacks vs others **")
        print(f"** Escape DC: {grapple_dc} (STR Athletics or DEX Acrobatics check) **")
        
        # Note: PCs don't apply Restrained like Giant Octopus does
        return True


# Factory functions for easy creation
def create_unarmed_damage_action():
    """Create Unarmed Strike (Damage) action."""
    return UnarmedStrikeAction("damage")

def create_unarmed_grapple_action():
    """Create Unarmed Strike (Grapple) action."""
    return UnarmedStrikeAction("grapple")

def create_unarmed_shove_action():
    """Create Unarmed Strike (Shove) action."""
    return UnarmedStrikeAction("shove")
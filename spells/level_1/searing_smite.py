# File: spells/level_1/searing_smite.py
from ..base_spell import Spell
from core import roll


class SearingSmite(Spell):
    def __init__(self):
        super().__init__(
            name="Searing Smite",
            level=1,
            school="Evocation",
            casting_time="1 Bonus Action (immediately after hitting with melee weapon or unarmed strike)",
            requires_concentration=False,  # PHB 2024: No longer requires concentration!
            damage_type="Fire",
            attack_save="CON Save"
        )

    def cast(self, caster, target, spell_level=1):
        """PHB 2024: Cast immediately after hitting with melee attack - adds immediate and ongoing damage."""
        if not target:
            return False

        # FIXED: Check if target already has Searing Smite effect
        if hasattr(target, 'searing_smite_effect') and target.searing_smite_effect.get('active', False):
            print(f"** {target.name} is already under the effects of Searing Smite! **")
            print(f"** Spell slot expended, but effect does not stack — Searing Smite remains at original intensity **")
            return False  # Don't apply new effect, but spell slot is still consumed

        # Calculate damage per spell level
        dice_count = spell_level  # 1d6 at 1st, 2d6 at 2nd, etc.
        
        # PHB 2024: "As you hit the target, it takes an extra 1d6 Fire damage from the attack"
        immediate_damage = 0
        for _ in range(dice_count):
            immediate_damage += roll('1d6')
        
        print(f"** SEARING SMITE: {immediate_damage} extra fire damage ({dice_count}d6) added to the attack! **")
        
        # Apply immediate damage (this is added to the weapon attack damage)
        target.take_damage(immediate_damage, attacker=caster)
        
        # Set up ongoing fire damage effect for subsequent turns
        target.searing_smite_effect = {
            'active': True,
            'dice_count': dice_count,
            'caster': caster,
            'save_dc': caster.get_spell_save_dc()
        }
        print(f"** {target.name} is wreathed in flames! Takes {dice_count}d6 fire damage each turn until CON save succeeds **")
        
        if spell_level > 1:
            print(f"** Upcast at level {spell_level}: {dice_count}d6 damage per turn **")
        
        return True

    def process_start_of_turn(self, target):
        """Process Searing Smite damage at start of target's turn."""
        if not hasattr(target, 'searing_smite_effect') or not target.searing_smite_effect['active']:
            return

        effect = target.searing_smite_effect
        dice_count = effect['dice_count']
        save_dc = effect['save_dc']
        caster = effect['caster']

        # Deal ongoing fire damage
        ongoing_damage = 0
        for _ in range(dice_count):
            ongoing_damage += roll('1d6')

        print(f"** {target.name} takes {ongoing_damage} fire damage ({dice_count}d6) from Searing Smite! **")
        target.take_damage(ongoing_damage, attacker=caster)

        # Constitution saving throw to end the effect
        if target.is_alive:
            print(f"** {target.name} makes a Constitution saving throw to extinguish the flames **")
            if target.make_saving_throw('con', save_dc):
                print(f"** {target.name} succeeds and extinguishes the searing flames! **")
                self.end_effect(target)
            else:
                print(f"** {target.name} fails and continues burning! **")

    def end_effect(self, target):
        """End the Searing Smite effect on a target."""
        if hasattr(target, 'searing_smite_effect'):
            target.searing_smite_effect['active'] = False
            del target.searing_smite_effect
            print(f"** Searing Smite effect ends on {target.name} **")


# Create the instance
searing_smite = SearingSmite()
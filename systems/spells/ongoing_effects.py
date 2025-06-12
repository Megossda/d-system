# File: systems/spells/ongoing_effects.py
"""Global ongoing spell effects system."""

from core import roll

def process_ongoing_spell_effects(creature):
    """Process ongoing spell effects like Searing Smite."""
    if hasattr(creature, 'searing_smite_effect') and creature.searing_smite_effect.get('active', False):
        process_searing_smite_effect(creature)

def process_searing_smite_effect(creature):
    """Process Searing Smite ongoing effect."""
    effect = creature.searing_smite_effect
    dice_count = effect['dice_count']
    save_dc = effect['save_dc']
    caster = effect['caster']
    
    # Deal ongoing fire damage
    ongoing_damage = 0
    for _ in range(dice_count):
        ongoing_damage += roll('1d6')
    
    print(f"** {creature.name} takes {ongoing_damage} fire damage ({dice_count}d6) from Searing Smite! **")
    creature.take_damage(ongoing_damage, attacker=caster)
    
    # Constitution saving throw to end the effect
    if creature.is_alive:
        if creature.make_saving_throw('con', save_dc):
            print(f"** {creature.name} extinguishes the searing flames! **")
            creature.searing_smite_effect['active'] = False
            del creature.searing_smite_effect
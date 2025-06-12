# File: systems/combat/saving_throws.py
"""Global saving throw system."""

from core import roll_d20, get_ability_modifier

def make_creature_save(creature, ability, dc, proficiency_bonus=None):
    """Make a saving throw using global system."""
    print(f"--- {creature.name} makes a DC {dc} {ability.upper()} saving throw! ---")
    
    roll_val, _ = roll_d20()
    modifier = get_ability_modifier(creature.stats[ability])
    
    # Add proficiency if specified
    if proficiency_bonus is None:
        # Check if creature has save proficiency
        save_name = ability.capitalize()
        if save_name in getattr(creature, 'save_proficiencies', []):
            proficiency_bonus = creature.get_proficiency_bonus()
        else:
            proficiency_bonus = 0
    
    total = roll_val + modifier + proficiency_bonus
    
    log = f"Save: {roll_val} (1d20) +{modifier} ({ability.upper()})"
    if proficiency_bonus > 0:
        log += f" +{proficiency_bonus} (Prof)"
    log += f" = {total}"
    print(log)
    
    success = total >= dc
    print("Save successful!" if success else "Save failed.")
    return success
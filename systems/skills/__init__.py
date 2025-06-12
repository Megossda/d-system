# File: systems/skills/__init__.py
"""Global skill system."""

from core import get_ability_modifier

def calculate_skill_bonus(creature, skill):
    """Calculate skill bonus using global system."""
    ability_map = {
        'Athletics': 'str',
        'Acrobatics': 'dex', 
        'Sleight of Hand': 'dex',
        'Stealth': 'dex',
        'Arcana': 'int',
        'History': 'int',
        'Investigation': 'int',
        'Nature': 'int',
        'Religion': 'int',
        'Animal Handling': 'wis',
        'Insight': 'wis',
        'Medicine': 'wis',
        'Perception': 'wis',
        'Survival': 'wis',
        'Deception': 'cha',
        'Intimidation': 'cha',
        'Performance': 'cha',
        'Persuasion': 'cha'
    }
    
    if skill not in ability_map:
        return 0
    
    ability_mod = get_ability_modifier(creature.stats[ability_map[skill]])
    
    if skill in getattr(creature, 'skill_proficiencies', []):
        return ability_mod + creature.get_proficiency_bonus()
    
    return ability_mod
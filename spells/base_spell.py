# File: spells/base_spell.py
"""Base spell class."""

class BaseSpell:
    """Base class for all spells."""
    
    def __init__(self, name, level, school, casting_time="1 Action", 
                 range_type="60 feet", components="V, S", duration="Instantaneous",
                 damage_type=None, save_type=None):
        self.name = name
        self.level = level
        self.school = school
        self.casting_time = casting_time
        self.range_type = range_type
        self.components = components
        self.duration = duration
        self.damage_type = damage_type
        self.save_type = save_type
    
    def cast(self, caster, targets, spell_level, action_type="ACTION"):
        """Cast the spell - must be overridden."""
        raise NotImplementedError("Each spell must implement cast method")
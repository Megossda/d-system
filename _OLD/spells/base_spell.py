class Spell:
    """A base class for all spells."""
    def __init__(self, name, level, school, casting_time="1 Action", requires_concentration=False, damage_type=None, attack_save="None"):
        self.name = name
        self.level = level
        self.school = school
        self.casting_time = casting_time
        self.requires_concentration = requires_concentration
        self.damage_type = damage_type
        self.attack_save = attack_save

    def cast(self, caster, target=None):
        """The primary effect of casting the spell."""
        # This method is meant to be overridden by each specific spell.
        raise NotImplementedError("Each spell must have its own 'cast' method.")


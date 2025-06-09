class Armor:
    """A base class for all armor and shields."""
    def __init__(self, name, category, base_ac=0, ac_bonus=0, strength_requirement=0, stealth_disadvantage=False):
        self.name = name
        self.category = category
        self.base_ac = base_ac
        self.ac_bonus = ac_bonus
        self.strength_requirement = strength_requirement
        self.stealth_disadvantage = stealth_disadvantage

class Weapon:
    """A base class for all weapons, including their properties."""
    def __init__(self, name, damage_dice, damage_type, properties=None, reach=5):
        self.name = name
        self.damage_dice = damage_dice
        self.damage_type = damage_type
        self.properties = properties or []
        self.reach = reach # Default reach is 5 feet
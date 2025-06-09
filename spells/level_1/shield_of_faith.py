# File: spells/level_1/shield_of_faith.py
from ..base_spell import Spell


class ShieldOfFaith(Spell):
    """Shield of Faith spell - grants +2 AC bonus."""

    def __init__(self):
        super().__init__(
            name="Shield of Faith",
            level=1,
            school="Abjuration",
            casting_time="1 Bonus Action",
            requires_concentration=True,
            attack_save="None"
        )

    def cast(self, caster, target=None):
        """Grant +2 AC bonus to a creature within 60 feet."""
        target_to_affect = target or caster

        if not target_to_affect:
            return False

        # PHB 2024: 60-foot range (in full implementation, would check distance)
        # For now, assume target is within range if provided

        # Apply AC bonus
        if not hasattr(target_to_affect, 'shield_of_faith_bonus'):
            target_to_affect.shield_of_faith_bonus = 0

        if target_to_affect.shield_of_faith_bonus == 0:
            target_to_affect.shield_of_faith_bonus = 2
            target_to_affect.ac += 2
            print(f"** {target_to_affect.name} is surrounded by a shimmering field of protection! **")
            print(f"** AC increased from {target_to_affect.ac - 2} to {target_to_affect.ac} (+2 Shield of Faith) **")
        else:
            print(f"** {target_to_affect.name} is already protected by Shield of Faith! **")
            return False

        # Set up concentration
        caster.start_concentrating(self)

        print(f"** Duration: Concentration, up to 10 minutes **")
        print(f"** Range: 60 feet | Material Component: Prayer scroll **")

        return True

    def end_concentration(self, target):
        """Called when concentration is broken."""
        if hasattr(target, 'shield_of_faith_bonus') and target.shield_of_faith_bonus > 0:
            target.ac -= target.shield_of_faith_bonus
            target.shield_of_faith_bonus = 0
            print(f"** The shimmering field around {target.name} fades away **")
            print(f"** {target.name}'s AC returns to {target.ac} **")


# Create the instance
shield_of_faith = ShieldOfFaith()
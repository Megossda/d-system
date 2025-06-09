# File: spells/level_1/bless.py
from ..base_spell import Spell
from core import roll


class Bless(Spell):
    def __init__(self):
        super().__init__(
            name="Bless",
            level=1,
            school="Enchantment",
            casting_time="1 Action",
            requires_concentration=True,
            attack_save="None"
        )

    def cast(self, caster, targets=None, spell_level=1):
        """PHB 2024: Bless up to 3 creatures (+1 per higher level), +1d4 to attacks and saves."""
        if not targets:
            # Default to blessing the caster if no targets specified
            targets = [caster]
        elif not isinstance(targets, list):
            targets = [targets]

        # Calculate max targets based on spell level
        max_targets = 3 + (spell_level - 1)  # 3 at 1st level, +1 per higher level

        # Limit to available targets within range (30 feet)
        valid_targets = []
        for target in targets[:max_targets]:
            # In a full implementation, would check 30-foot range
            # For now, assume all provided targets are valid
            if target and target.is_alive:
                valid_targets.append(target)

        if not valid_targets:
            print(f"** No valid targets for {self.name}! **")
            return False

        # Apply bless effect to each target
        blessed_names = []
        for target in valid_targets:
            if not hasattr(target, 'bless_bonus'):
                target.bless_bonus = 0

            if target.bless_bonus == 0:
                target.bless_bonus = 1  # Flag that they have bless (1d4 bonus)
                blessed_names.append(target.name)
            else:
                print(f"** {target.name} is already blessed! **")

        if blessed_names:
            # Set up concentration
            caster.start_concentrating(self)

            target_text = ", ".join(blessed_names)
            print(f"** {caster.name} blesses: {target_text} **")
            print(f"** Blessed creatures add 1d4 to attack rolls and saving throws for 1 minute **")

            if spell_level > 1:
                print(f"** Upcast at level {spell_level}: {len(valid_targets)} targets blessed **")

            return True
        else:
            print(f"** No new targets to bless! **")
            return False

    def apply_bless_bonus(self, target):
        """Apply the 1d4 bonus when a blessed creature makes an attack or save."""
        if hasattr(target, 'bless_bonus') and target.bless_bonus > 0:
            bonus = roll('1d4')
            print(f"** {target.name} adds {bonus} (1d4 Bless bonus) **")
            return bonus
        return 0


# Create the instance
bless = Bless()
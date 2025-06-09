# File: spells/level_1/heroism.py
from ..base_spell import Spell
from core import get_ability_modifier


class Heroism(Spell):
    """Heroism spell - PHB 2024 version with ongoing temporary hit points."""

    def __init__(self):
        super().__init__(
            name="Heroism",
            level=1,
            school="Enchantment",
            casting_time="1 Action",
            requires_concentration=True,
            attack_save="None"
        )

    def cast(self, caster, targets=None, spell_level=1):
        """PHB 2024: Grant immunity to frightened + temp HP each turn. Can target multiple creatures when upcast."""
        if not targets:
            targets = [caster]  # Default to self if no target specified
        elif not isinstance(targets, list):
            targets = [targets]

        # Calculate max targets based on spell level
        max_targets = 1 + (spell_level - 1)  # 1 at 1st level, +1 per higher level

        # Limit to available targets (must be willing)
        valid_targets = []
        for target in targets[:max_targets]:
            if target and target.is_alive:
                valid_targets.append(target)

        if not valid_targets:
            print(f"** No valid targets for {self.name}! **")
            return False

        # Calculate temp HP per turn
        temp_hp_per_turn = caster.get_spellcasting_modifier()
        if temp_hp_per_turn < 1:
            temp_hp_per_turn = 1  # Minimum 1

        # Apply heroism effect to each target
        heroism_targets = []
        for target in valid_targets:
            # Mark target as having heroism effect
            target.heroism_active = True
            target.heroism_temp_hp_per_turn = temp_hp_per_turn

            # Grant immediate immunity to frightened
            target.is_immune_to_frightened = True

            # Grant initial temporary hit points
            if not hasattr(target, 'temp_hp'):
                target.temp_hp = 0

            # PHB 2024: Temp HP don't stack, but heroism refreshes each turn
            if temp_hp_per_turn > target.temp_hp:
                target.temp_hp = temp_hp_per_turn
                print(f"** {target.name} gains {temp_hp_per_turn} temporary hit points! **")

            heroism_targets.append(target.name)

        if heroism_targets:
            # Set up concentration
            caster.start_concentrating(self)

            target_text = ", ".join(heroism_targets)
            print(f"** {caster.name} imbues {target_text} with heroic bravery! **")
            print(
                f"** Targets are immune to being frightened and gain {temp_hp_per_turn} temp HP at start of each turn **")

            if spell_level > 1:
                print(f"** Upcast at level {spell_level}: {len(valid_targets)} creatures affected **")

            return True
        else:
            print(f"** No new targets to affect with Heroism! **")
            return False

    def process_turn_start(self, target):
        """Called at the start of each turn for targets under heroism effect."""
        if hasattr(target, 'heroism_active') and target.heroism_active:
            temp_hp_gain = target.heroism_temp_hp_per_turn

            # PHB 2024: Gain temp HP at start of each turn
            if not hasattr(target, 'temp_hp'):
                target.temp_hp = 0

            # Don't stack, but refresh to full amount
            if temp_hp_gain > target.temp_hp:
                target.temp_hp = temp_hp_gain
                print(f"** {target.name} gains {temp_hp_gain} temporary hit points from Heroism! **")
            else:
                print(f"** {target.name} retains {target.temp_hp} temporary hit points from Heroism **")

    def end_concentration(self, targets):
        """Called when concentration is broken."""
        for target in targets:
            if hasattr(target, 'heroism_active'):
                target.heroism_active = False
                target.is_immune_to_frightened = False
                if hasattr(target, 'heroism_temp_hp_per_turn'):
                    del target.heroism_temp_hp_per_turn
                print(f"** {target.name} is no longer under the effects of Heroism **")


# Create the instance
heroism = Heroism()
# File: systems/paladin/channel_divinity.py
from core import get_ability_modifier


class ChannelDivinityOption:
    """Base class for all Channel Divinity options."""

    def __init__(self, name, action_type="Bonus Action", description=""):
        self.name = name
        self.action_type = action_type  # "Bonus Action", "Magic Action", "Action", etc.
        self.description = description

    def can_use(self, character):
        """Check if this option can be used (override for specific requirements)."""
        return character.channel_divinity_uses > 0

    def execute(self, character, target=None, **kwargs):
        """Execute the Channel Divinity option (override in subclasses)."""
        if not self.can_use(character):
            print(f"{character.name} has no Channel Divinity uses remaining!")
            return False

        character.channel_divinity_uses -= 1
        print(
            f"** {character.name} uses Channel Divinity: {self.name} ({character.channel_divinity_uses} uses remaining) **")
        return self._perform_effect(character, target, **kwargs)

    def _perform_effect(self, character, target=None, **kwargs):
        """Override this method with the actual effect."""
        raise NotImplementedError("Subclasses must implement _perform_effect")


class DivineSenseOption(ChannelDivinityOption):
    """PHB 2024 Divine Sense - detects celestials, fiends, and undead."""

    def __init__(self):
        super().__init__(
            name="Divine Sense",
            action_type="Bonus Action",
            description="Detect Celestials, Fiends, and Undead within 60 feet for 10 minutes"
        )

    def _perform_effect(self, character, target=None, **kwargs):
        """Activate Divine Sense."""
        print(f"** {character.name}'s awareness expands to detect otherworldly creatures! **")
        print(
            f"** For the next 10 minutes, {character.name} knows the location of any Celestial, Fiend, or Undead within 60 feet **")
        print(f"** Also detects consecrated or desecrated places within the same radius **")

        # In a full implementation, this would set a timer/effect
        # For now, just announce the effect
        character.divine_sense_active = True
        character.divine_sense_duration = 10  # 10 minutes (could track this in combat rounds)

        return True


class PaladinChannelDivinityMixin:
    """Mixin to add Paladin Channel Divinity functionality."""

    def init_channel_divinity(self):
        """Initialize Channel Divinity system (call this in Paladin __init__)."""
        self.channel_divinity_uses = self.get_channel_divinity_uses()
        self.channel_divinity_options = []
        self.divine_sense_active = False
        self.divine_sense_duration = 0

        # All Paladins get Divine Sense
        self.add_channel_divinity_option(DivineSenseOption())

    def get_channel_divinity_uses(self):
        """Get number of Channel Divinity uses based on level."""
        if self.level < 3:
            return 0  # No Channel Divinity before level 3
        elif self.level < 11:
            return 2  # 2 uses from levels 3-10
        else:
            return 3  # 3 uses from level 11+

    def add_channel_divinity_option(self, option):
        """Add a new Channel Divinity option."""
        if isinstance(option, ChannelDivinityOption):
            self.channel_divinity_options.append(option)
        else:
            raise ValueError("Must be a ChannelDivinityOption instance")

    def use_channel_divinity(self, option_name, target=None, **kwargs):
        """Use a specific Channel Divinity option by name."""
        for option in self.channel_divinity_options:
            if option.name == option_name:
                return option.execute(self, target, **kwargs)

        print(f"{self.name} doesn't have the Channel Divinity option: {option_name}")
        return False

    def get_spell_save_dc(self):
        """Get spell save DC for Channel Divinity effects."""
        return 8 + self.get_proficiency_bonus() + get_ability_modifier(self.stats['cha'])

    def short_rest_recovery(self):
        """Recover one Channel Divinity use on short rest."""
        max_uses = self.get_channel_divinity_uses()
        if self.channel_divinity_uses < max_uses:
            self.channel_divinity_uses += 1
            print(f"** {self.name} recovers 1 Channel Divinity use ({self.channel_divinity_uses}/{max_uses}) **")

    def long_rest_recovery(self):
        """Recover all Channel Divinity uses on long rest."""
        self.channel_divinity_uses = self.get_channel_divinity_uses()
        print(f"** {self.name} recovers all Channel Divinity uses ({self.channel_divinity_uses}) **")

    def list_channel_divinity_options(self):
        """List all available Channel Divinity options."""
        print(f"\n{self.name}'s Channel Divinity Options ({self.channel_divinity_uses} uses remaining):")
        for option in self.channel_divinity_options:
            status = "✓" if option.can_use(self) else "✗"
            print(f"  {status} {option.name} ({option.action_type}): {option.description}")
        print()
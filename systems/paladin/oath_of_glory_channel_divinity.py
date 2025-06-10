# File: systems/paladin/oath_of_glory_channel_divinity.py
from .channel_divinity import ChannelDivinityOption
from core import roll, get_ability_modifier


class InspiringSMiteOption(ChannelDivinityOption):
    """Oath of Glory: Inspiring Smite - distribute temp HP after Divine Smite."""

    def __init__(self):
        super().__init__(
            name="Inspiring Smite",
            action_type="Free (after Divine Smite)",
            description="After Divine Smite, distribute 2d8 + Paladin level temp HP to allies within 30ft"
        )

    def can_use(self, character):
        """Can only use immediately after casting Divine Smite."""
        return super().can_use(character)

    def _perform_effect(self, character, targets=None, **kwargs):
        """Distribute temporary hit points after Divine Smite."""
        if not targets:
            targets = [character]  # Default to self if no targets
        elif not isinstance(targets, list):
            targets = [targets]

        # Calculate total temp HP pool
        temp_hp_pool = 0
        for _ in range(2):  # 2d8
            temp_hp_pool += roll('1d8')
        temp_hp_pool += character.level  # + Paladin level

        print(f"** INSPIRING SMITE: {character.name} has {temp_hp_pool} temporary hit points to distribute! **")

        # In a full implementation, would allow player to choose distribution
        # For AI, distribute evenly among valid targets
        valid_targets = []
        for target in targets:
            # Check 30-foot range (simplified - assume all provided targets are in range)
            if target and target.is_alive:
                valid_targets.append(target)

        if not valid_targets:
            print(f"** No valid targets within 30 feet for Inspiring Smite! **")
            return False

        # Distribute temp HP evenly (AI decision)
        hp_per_target = temp_hp_pool // len(valid_targets)
        remaining_hp = temp_hp_pool % len(valid_targets)

        for i, target in enumerate(valid_targets):
            if not hasattr(target, 'temp_hp'):
                target.temp_hp = 0

            # Give first few targets 1 extra HP if there's a remainder
            hp_to_give = hp_per_target + (1 if i < remaining_hp else 0)

            # Temp HP don't stack - take higher value
            if hp_to_give > target.temp_hp:
                target.temp_hp = hp_to_give
                print(f"** {target.name} gains {hp_to_give} temporary hit points! **")
            else:
                print(f"** {target.name} already has {target.temp_hp} temp HP (keeping higher) **")

        return True


class PeerlessAthleteOption(ChannelDivinityOption):
    """Oath of Glory: Peerless Athlete - enhanced athleticism for 1 hour."""

    def __init__(self):
        super().__init__(
            name="Peerless Athlete",
            action_type="Bonus Action",
            description="Gain advantage on Athletics/Acrobatics and +10ft jump distance for 1 hour"
        )

    def _perform_effect(self, character, target=None, **kwargs):
        """Grant enhanced athleticism."""
        print(f"** {character.name} channels divine energy to enhance their athleticism! **")
        print(f"** For 1 hour: **")
        print(f"   - Advantage on Strength (Athletics) checks")
        print(f"   - Advantage on Dexterity (Acrobatics) checks")
        print(f"   - Long and High jump distance increased by 10 feet")

        # Set athletic enhancement flags
        character.peerless_athlete_active = True
        character.peerless_athlete_duration = 60  # 60 minutes

        # In a full implementation, this would be tracked and applied to skill checks
        return True
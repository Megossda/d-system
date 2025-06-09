from core import roll


class Effect:
    """A base class for any ongoing effect in the game."""

    def __init__(self, name, duration):
        self.name = name
        self.duration = duration

    def apply(self, target):
        """Logic that triggers on the affected creature's turn."""
        pass

    def tick_down(self):
        """Reduces the duration of the effect."""
        self.duration -= 1


class SearingSmiteEffect(Effect):
    """The ongoing fire damage from the Searing Smite spell."""

    def __init__(self, caster):
        super().__init__(name="Searing Smite", duration=10)
        self.caster = caster
        self.save_dc = caster.get_spell_save_dc()

    def apply(self, target):
        """Deals fire damage and allows a save to end the effect."""
        damage = roll('1d6')
        print(f"** {target.name} takes {damage} fire damage from Searing Smite! **")
        target.take_damage(damage)

        print(f"{target.name} must make a Constitution save to end the burning.")
        if target.make_saving_throw('con', self.save_dc):
            print(f"{target.name} succeeds and extinguishes the flames!")
            self.duration = 0  # End the effect
        else:
            print(f"{target.name} fails to extinguish the flames.")

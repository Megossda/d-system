from core import roll, get_ability_modifier
from base_character import Character

class Fighter(Character):
    """
    A Fighter class featuring Second Wind for self-healing.
    """
    def __init__(self, name, level, hp, ac, stats, weapon_damage):
        super().__init__(name, level, hp, ac, stats, weapon_damage)
        self.second_wind_used = False

    def use_second_wind(self):
        """
        Uses Second Wind to heal for 1d10 + fighter level.
        Can only be used once per combat.
        """
        if not self.second_wind_used:
            self.second_wind_used = True
            healing_amount = roll('1d10') + self.level
            self.hp = min(self.max_hp, self.hp + healing_amount)
            print(f"** {self.name} uses Second Wind, healing for {healing_amount} HP! **")
            print(f"{self.name}'s HP is now {self.hp}/{self.max_hp}.")
        else:
            print(f"{self.name} has already used Second Wind.")

    # In a more complex simulation, you might call use_second_wind()
    # when the Fighter is low on health.

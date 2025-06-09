from core import roll_d20, roll, get_ability_modifier
from base_character import Character


class Wizard(Character):
    """
    A Wizard class that attacks with a cantrip (Fire Bolt) using Intelligence.
    """

    def __init__(self, name, level, hp, ac, stats, weapon_damage=None):
        # Wizards don't typically use weapons, so we default weapon_damage to None
        super().__init__(name, level, hp, ac, stats, weapon_damage)
        self.cantrip_damage = '1d10'  # Fire Bolt

    def get_attack_modifier(self):
        """Overrides to use Intelligence for spell attack rolls."""
        return get_ability_modifier(self.stats['int'])

    def get_damage_modifier(self):
        """Wizards don't add their ability modifier to cantrip damage by default."""
        return 0

    def attack(self, target):
        """Overrides attack to cast a spell instead of using a weapon."""
        if not self.is_alive: return

        print(f"{self.name} casts Fire Bolt at {target.name}!")

        use_advantage = self.has_advantage and not self.has_disadvantage
        use_disadvantage = self.has_disadvantage and not self.has_advantage
        attack_roll, all_rolls = roll_d20(advantage=use_advantage, disadvantage=use_disadvantage)
        self.has_advantage = False
        self.has_disadvantage = False

        if attack_roll == 1 and len(all_rolls) == 1:
            print(f"{self.name} rolled a 1 (1d20)... CRITICAL MISS!")
            return

        is_crit = (attack_roll == 20)

        log_message = f"{self.name} rolled a spell attack: "
        if len(all_rolls) > 1:
            state = "advantage" if use_advantage else "disadvantage"
            log_message += f"rolls of {all_rolls} ({state}) -> took {attack_roll} (1d20)"
        else:
            log_message += f"{attack_roll} (1d20)"

        attack_modifier = self.get_attack_modifier()
        total_attack = attack_roll + attack_modifier
        log_message += f" + {attack_modifier} (INT) = {total_attack}"
        print(log_message)

        if is_crit or total_attack >= target.ac:
            if is_crit:
                print(">>> CRITICAL HIT! <<<")
            else:
                print("The attack hits!")

            damage_die_roll = roll(self.cantrip_damage)
            total_damage = damage_die_roll
            damage_breakdown = f"{damage_die_roll} [{self.cantrip_damage}]"

            if is_crit:
                crit_damage_roll = roll(self.cantrip_damage)
                total_damage += crit_damage_roll
                damage_breakdown += f" + {crit_damage_roll} [Crit]"

            print(f"{self.name} deals {total_damage} damage. ({damage_breakdown})")
            target.take_damage(total_damage)
        else:
            print(f"The attack misses {target.name}'s AC of {target.ac}.")

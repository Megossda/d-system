from core import roll_d20, roll, get_ability_modifier
from base_character import Character


class Rogue(Character):
    """
    A Rogue class that can use Sneak Attack and uses Dexterity for attacks.
    """

    def get_attack_modifier(self):
        """Overrides to use Dexterity for attack rolls."""
        return get_ability_modifier(self.stats['dex'])

    def get_damage_modifier(self):
        """Overrides to use Dexterity for damage rolls."""
        return get_ability_modifier(self.stats['dex'])

    def get_sneak_attack_damage(self):
        """Calculates sneak attack damage dice based on rogue level."""
        # 1d6 at level 1, 2d6 at 3, 3d6 at 5, etc.
        return f"{(self.level + 1) // 2}d6"

    def attack(self, target):
        """Overrides base attack to add Sneak Attack damage on advantage."""
        if not self.is_alive: return

        print(f"{self.name} attacks {target.name}!")

        use_advantage = self.has_advantage and not self.has_disadvantage
        use_disadvantage = self.has_disadvantage and not self.has_advantage
        attack_roll, all_rolls = roll_d20(advantage=use_advantage, disadvantage=use_disadvantage)
        self.has_advantage = False
        self.has_disadvantage = False

        if attack_roll == 1 and len(all_rolls) == 1:
            print(f"{self.name} rolled a 1 (1d20)... CRITICAL MISS!")
            return

        is_crit = (attack_roll == 20)

        log_message = f"{self.name} rolled an attack: "
        if len(all_rolls) > 1:
            state = "advantage" if use_advantage else "disadvantage"
            log_message += f"rolls of {all_rolls} ({state}) -> took {attack_roll} (1d20)"
        else:
            log_message += f"{attack_roll} (1d20)"

        attack_modifier = self.get_attack_modifier()
        total_attack = attack_roll + attack_modifier
        log_message += f" + {attack_modifier} (DEX) = {total_attack}"
        print(log_message)

        if is_crit or total_attack >= target.ac:
            if is_crit:
                print(">>> CRITICAL HIT! <<<")
            else:
                print("The attack hits!")

            damage_die_roll = roll(self.weapon_damage)
            damage_modifier = self.get_damage_modifier()
            damage_breakdown_parts = [f"{damage_die_roll} [{self.weapon_damage}]"]
            total_damage = damage_die_roll

            if is_crit:
                crit_damage_roll = roll(self.weapon_damage)
                total_damage += crit_damage_roll
                damage_breakdown_parts.append(f"{crit_damage_roll} [Crit]")

            # --- SNEAK ATTACK LOGIC ---
            if use_advantage:
                sneak_dice = self.get_sneak_attack_damage()
                sneak_damage = roll(sneak_dice)
                print(f"** {self.name} gets a SNEAK ATTACK! **")
                total_damage += sneak_damage
                damage_breakdown_parts.append(f"{sneak_damage} [{sneak_dice} Sneak]")

                if is_crit:  # Double sneak attack dice on crit
                    sneak_crit_damage = roll(sneak_dice)
                    total_damage += sneak_crit_damage
                    damage_breakdown_parts.append(f"{sneak_crit_damage} [Sneak Crit]")
            # --- END SNEAK ATTACK LOGIC ---

            total_damage = max(1, total_damage + damage_modifier)
            damage_breakdown_parts.append(f"{damage_modifier} [DEX]")
            damage_breakdown = " + ".join(damage_breakdown_parts)

            print(f"{self.name} deals a total of {total_damage} damage. ({damage_breakdown})")
            target.take_damage(total_damage)
        else:
            print(f"The attack misses {target.name}'s AC of {target.ac}.")

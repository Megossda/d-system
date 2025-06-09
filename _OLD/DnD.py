import random


# --- Core Dice and Game Functions ---

def roll_d20(advantage=False, disadvantage=False):
    """
    Rolls a d20, applying advantage or disadvantage.
    Returns the chosen roll and a list of all rolls.
    """
    roll1 = random.randint(1, 20)

    # Advantage and disadvantage cancel each other out, or if neither apply.
    if not (advantage ^ disadvantage):
        return roll1, [roll1]

    roll2 = random.randint(1, 20)
    rolls = sorted([roll1, roll2])

    if advantage:
        return rolls[1], rolls  # Higher roll
    else:  # Disadvantage
        return rolls[0], rolls  # Lower roll


def roll(dice_string):
    """Rolls dice based on a string like '1d8' or '2d6'."""
    try:
        num_dice, die_type = map(int, dice_string.split('d'))
        return sum(random.randint(1, die_type) for _ in range(num_dice))
    except ValueError:
        print(f"Error: Invalid dice string format '{dice_string}'")
        return 0


def get_ability_modifier(score):
    """Calculates the ability modifier for a given ability score."""
    return (score - 10) // 2


# --- Base Character Class ---

class Character:
    """Represents a generic character or monster in the D&D simulation."""

    def __init__(self, name, level, hp, ac, stats, weapon_damage):
        self.name = name
        self.level = level
        self.max_hp = hp
        self.hp = hp
        self.ac = ac
        self.stats = stats
        self.weapon_damage = weapon_damage
        self.is_alive = True
        self.initiative = 0
        # --- NEW: Advantage/Disadvantage Flags ---
        self.has_advantage = False
        self.has_disadvantage = False

    def roll_initiative(self):
        """Rolls a d20, adds Dexterity modifier, and stores the result."""
        roll, _ = roll_d20()  # Initiative doesn't use advantage/disadvantage yet
        modifier = get_ability_modifier(self.stats['dex'])
        self.initiative = roll + modifier
        print(f"{self.name} rolls for initiative: {roll} (1d20) + {modifier} (DEX) = {self.initiative}")

    def get_attack_modifier(self):
        """Determines the modifier for an attack roll (using Strength)."""
        return get_ability_modifier(self.stats['str'])

    def get_damage_modifier(self):
        """Determines the modifier for a damage roll (using Strength)."""
        return get_ability_modifier(self.stats['str'])

    def attack(self, target):
        """Performs an attack, now with Advantage/Disadvantage logic."""
        if not self.is_alive: return

        print(f"{self.name} attacks {target.name}!")

        # Check for advantage/disadvantage on this attack
        use_advantage = self.has_advantage and not self.has_disadvantage
        use_disadvantage = self.has_disadvantage and not self.has_advantage

        attack_roll, all_rolls = roll_d20(advantage=use_advantage, disadvantage=use_disadvantage)

        # Reset flags after they are used for an attack
        self.has_advantage = False
        self.has_disadvantage = False

        # --- CRITICAL HIT/MISS LOGIC ---
        if attack_roll == 1 and len(all_rolls) == 1:  # Only a natural 1 on a straight roll is a crit miss
            print(f"{self.name} rolled a 1 (1d20)... CRITICAL MISS!")
            return

        is_crit = (attack_roll == 20)

        # --- Build descriptive log message for the roll ---
        log_message = f"{self.name} rolled an attack: "
        if len(all_rolls) > 1:
            state = "advantage" if use_advantage else "disadvantage"
            log_message += f"rolls of {all_rolls} ({state}) -> took {attack_roll} (1d20)"
        else:
            log_message += f"{attack_roll} (1d20)"

        attack_modifier = self.get_attack_modifier()
        total_attack = attack_roll + attack_modifier
        log_message += f" + {attack_modifier} (STR) = {total_attack}"
        print(log_message)
        # --- End log message ---

        if is_crit or total_attack >= target.ac:
            if is_crit:
                print(">>> CRITICAL HIT! <<< It's an automatic hit and deals extra damage!")
            else:
                print("The attack hits!")

            damage_die_roll = roll(self.weapon_damage)
            damage_modifier = self.get_damage_modifier()
            total_damage = damage_die_roll
            damage_breakdown = f"{damage_die_roll} [{self.weapon_damage}]"

            if is_crit:
                crit_damage_roll = roll(self.weapon_damage)
                total_damage += crit_damage_roll
                damage_breakdown += f" + {crit_damage_roll} [Crit]"

            total_damage = max(1, total_damage + damage_modifier)
            damage_breakdown += f" + {damage_modifier} [STR]"

            print(f"{self.name} deals {total_damage} damage. ({damage_breakdown})")
            target.take_damage(total_damage)
        else:
            print(f"The attack misses {target.name}'s AC of {target.ac}.")

    def take_damage(self, damage):
        self.hp -= damage
        print(f"{self.name} takes {damage} damage and has {self.hp}/{self.max_hp} HP remaining.")
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False
            print(f"{self.name} has been defeated!")

    def __str__(self):
        stat_line = ", ".join(f"{k.capitalize()}: {v}" for k, v in self.stats.items())
        return (f"--- {self.name} (Lvl {self.level}) ---\n"
                f"HP: {self.hp}/{self.max_hp} | AC: {self.ac}\n"
                f"Stats: {stat_line}")


# --- Paladin Class ---

class Paladin(Character):
    """A Paladin class with the ability to use Divine Smite."""

    def __init__(self, name, level, hp, ac, stats, weapon_damage):
        super().__init__(name, level, hp, ac, stats, weapon_damage)
        self.spell_slots = self.get_max_spell_slots()

    def get_max_spell_slots(self):
        if self.level < 2: return 0
        if self.level < 3: return 2
        if self.level < 5: return 3
        return 4

    def attack(self, target):
        """Overrides base attack to add Smite, respecting Advantage/Disadvantage."""
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
        log_message += f" + {attack_modifier} (STR) = {total_attack}"
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

            if self.spell_slots > 0:
                self.spell_slots -= 1
                smite_dice = '2d8'
                smite_damage = roll(smite_dice)
                print(f"** {self.name} uses DIVINE SMITE! ({self.spell_slots} slot(s) left) **")
                total_damage += smite_damage
                damage_breakdown_parts.append(f"{smite_damage} [{smite_dice} Smite]")

                if is_crit:
                    smite_crit_damage = roll(smite_dice)
                    total_damage += smite_crit_damage
                    damage_breakdown_parts.append(f"{smite_crit_damage} [Smite Crit]")

            total_damage = max(1, total_damage + damage_modifier)
            damage_breakdown_parts.append(f"{damage_modifier} [STR]")
            damage_breakdown = " + ".join(damage_breakdown_parts)

            print(f"{self.name} deals a total of {total_damage} damage. ({damage_breakdown})")
            target.take_damage(total_damage)
        else:
            print(f"The attack misses {target.name}'s AC of {target.ac}.")


# --- Combat Simulation ---
def combat_simulation(char1, char2):
    print("===== COMBAT BEGINS =====")
    print(char1)
    print(char2)

    print("\n--- Rolling for Initiative ---")
    char1.roll_initiative()
    char2.roll_initiative()

    combatants = [char1, char2]
    combatants.sort(key=lambda c: c.initiative, reverse=True)

    print(f"--- {combatants[0].name} wins initiative and goes first! ---")

    turn = 1
    while all(c.is_alive for c in combatants):
        print(f"\n--- Round {turn} ---")

        for i in range(len(combatants)):
            attacker = combatants[i]
            # In a 2-person fight, the other person is the target.
            defender = combatants[(i + 1) % len(combatants)]

            if attacker.is_alive:
                attacker.attack(defender)
                if not defender.is_alive: break
                if i < len(combatants) - 1: print("-" * 15)

        if not all(c.is_alive for c in combatants): break
        turn += 1

    print("\n\n===== COMBAT ENDS =====")
    victor = next(c for c in combatants if c.is_alive)
    print(f"{victor.name} is the victor!")
    print(char1)
    print(char2)
    print("=======================")


if __name__ == "__main__":
    paladin = Paladin(
        name="Artus", level=3, hp=28, ac=18,
        stats={'str': 16, 'dex': 10, 'con': 14, 'int': 8, 'wis': 12, 'cha': 15},
        weapon_damage='1d8'
    )
    goblin = Character(
        name="Goblin Scout", level=1, hp=12, ac=14,
        stats={'str': 12, 'dex': 15, 'con': 10, 'int': 8, 'wis': 9, 'cha': 8},
        weapon_damage='1d6'
    )

    combat_simulation(paladin, goblin)

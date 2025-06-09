from classes.paladin import Paladin
from classes.subclasses.paladin_oaths import OathOfGlory
from enemies import Goblin, HobgoblinWarrior
from equipment.weapons.martial_melee import longsword
from equipment.armor.heavy import chain_mail
from equipment.armor.shields import shield
from equipment.weapons.longswords import plus_one_longsword

from combat import combat_simulation
from spells.level_1 import cure_wounds, searing_smite, guiding_bolt

if __name__ == "__main__":
    # --- ENEMY SELECTION ---
    available_enemies = {
        "1": {"name": "Goblin", "class": Goblin},
        "2": {"name": "Hobgoblin Warrior", "class": HobgoblinWarrior}
    }

    print("Choose your opponent:")
    for key, enemy_data in available_enemies.items():
        print(f"  {key}: {enemy_data['name']}")

    enemy_choice = None
    while enemy_choice not in available_enemies:
        enemy_choice = input("Enter the number of your choice: ")
        if enemy_choice not in available_enemies:
            print("Invalid choice. Please try again.")

    chosen_enemy_class = available_enemies[enemy_choice]["class"]
    enemy = chosen_enemy_class(position=40)
    print(f"\nYou will face a {enemy.name}!")
    # --- END ENEMY SELECTION ---

    # Create the player character
    paladin = Paladin(
        name="Artus",
        level=3,
        hp=28,
        stats={'str': 16, 'dex': 10, 'con': 14, 'int': 8, 'wis': 12, 'cha': 15},
        weapon=plus_one_longsword,
        armor=chain_mail,
        shield=shield,
        oath=OathOfGlory(),
        position=0,
        xp=0
    )

    paladin.prepare_spells([cure_wounds, searing_smite])

    combat_simulation([paladin, enemy])

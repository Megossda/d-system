# main.py
from characters.paladin import Paladin
from characters.subclasses.paladin_oaths import OathOfGlory
from enemies import Goblin, HobgoblinWarrior, GiantConstrictorSnake, GiantOctopus
from equipment.weapons.martial_melee import longsword
from equipment.armor.heavy import chain_mail
from equipment.armor.shields import shield
from equipment.weapons.longswords import plus_one_longsword
from combat import combat_simulation
from spells.level_1.cure_wounds import cure_wounds
from spells.level_1.searing_smite import searing_smite
from spells.level_1.guiding_bolt import guiding_bolt

if __name__ == "__main__":
    # --- ENEMY SELECTION ---
    available_enemies = {
        "1": {
            "name": "Goblin",
            "class": Goblin,
            "description": "CR 1/4 - Easy fight, good for testing"
        },
        "2": {
            "name": "Hobgoblin Warrior",
            "class": HobgoblinWarrior,
            "description": "CR 1/2 - Moderate challenge with ranged/melee tactics"
        },
        "3": {
            "name": "Giant Constrictor Snake",
            "class": GiantConstrictorSnake,
            "description": "CR 2 - Tough challenge with grappling and multiattack"
        },
        "4": {
            "name": "Giant Octopus", 
            "class": GiantOctopus,
            "description": "CR 1 - Multi-grappling beast with 8 tentacles and ink cloud"
        }
    }

    print("Choose your opponent:")
    for key, enemy_data in available_enemies.items():
        print(f"  {key}: {enemy_data['name']} - {enemy_data['description']}")

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
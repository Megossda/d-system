from equipment.weapons.base_weapon import Weapon

club = Weapon(name="Club", damage_dice="1d4", damage_type="Bludgeoning", properties=['Light'])
dagger = Weapon(name="Dagger", damage_dice="1d4", damage_type="Piercing", properties=['Finesse', 'Light', 'Thrown'])
greatclub = Weapon(name="Greatclub", damage_dice="1d8", damage_type="Bludgeoning", properties=['Two-Handed'])
handaxe = Weapon(name="Handaxe", damage_dice="1d6", damage_type="Slashing", properties=['Light', 'Thrown'])
javelin = Weapon(name="Javelin", damage_dice="1d6", damage_type="Piercing", properties=['Thrown'])
light_hammer = Weapon(name="Light Hammer", damage_dice="1d4", damage_type="Bludgeoning", properties=['Light', 'Thrown'])
mace = Weapon(name="Mace", damage_dice="1d6", damage_type="Bludgeoning")
quarterstaff = Weapon(name="Quarterstaff", damage_dice="1d6", damage_type="Bludgeoning", properties=['Versatile (1d8)'])
sickle = Weapon(name="Sickle", damage_dice="1d4", damage_type="Slashing", properties=['Light'])
spear = Weapon(name="Spear", damage_dice="1d6", damage_type="Piercing", properties=['Thrown', 'Versatile (1d8)'])

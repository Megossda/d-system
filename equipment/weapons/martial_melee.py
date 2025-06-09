from equipment.weapons.base_weapon import Weapon

longsword = Weapon(name="Longsword", damage_dice="1d8", damage_type="Slashing", properties=['Versatile (1d10)'])
scimitar = Weapon(name="Scimitar", damage_dice="1d6", damage_type="Slashing", properties=['Finesse', 'Light'])
# ... other martial melee weapons would be defined here

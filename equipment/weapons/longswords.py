from equipment.weapons.base_weapon import Weapon

# --- Unique and Magical Longswords ---

plus_one_longsword = Weapon(
    name="+1 Longsword",
    damage_dice="1d8",
    damage_type="Slashing",
    properties=['Versatile (1d10)', '+1 Magic Bonus']
)

warlords_flaming_longsword = Weapon(
    name="Warlord's Flaming Longsword",
    damage_dice="1d8",
    damage_type="Slashing",
    properties=['Versatile (1d10)', 'Deals 1d6 extra Fire damage']
)

class Weapon:
    """A base class for all weapons, including their properties."""
    def __init__(self, name, damage_dice, damage_type, properties=None):
        self.name = name
        self.damage_dice = damage_dice
        self.damage_type = damage_type
        self.properties = properties or []

# --- WEAPON LIST ---

# --- Simple Melee Weapons ---
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

# --- Simple Ranged Weapons ---
light_crossbow = Weapon(name="Light Crossbow", damage_dice="1d8", damage_type="Piercing", properties=['Ammunition', 'Loading', 'Two-Handed'])
dart = Weapon(name="Dart", damage_dice="1d4", damage_type="Piercing", properties=['Finesse', 'Thrown'])
shortbow = Weapon(name="Shortbow", damage_dice="1d6", damage_type="Piercing", properties=['Ammunition', 'Two-Handed'])
sling = Weapon(name="Sling", damage_dice="1d4", damage_type="Bludgeoning", properties=['Ammunition'])

# --- Martial Melee Weapons ---
battleaxe = Weapon(name="Battleaxe", damage_dice="1d8", damage_type="Slashing", properties=['Versatile (1d10)'])
flail = Weapon(name="Flail", damage_dice="1d8", damage_type="Bludgeoning")
glaive = Weapon(name="Glaive", damage_dice="1d10", damage_type="Slashing", properties=['Heavy', 'Reach', 'Two-Handed'])
greataxe = Weapon(name="Greataxe", damage_dice="1d12", damage_type="Slashing", properties=['Heavy', 'Two-Handed'])
greatsword = Weapon(name="Greatsword", damage_dice="2d6", damage_type="Slashing", properties=['Heavy', 'Two-Handed'])
halberd = Weapon(name="Halberd", damage_dice="1d10", damage_type="Slashing", properties=['Heavy', 'Reach', 'Two-Handed'])
lance = Weapon(name="Lance", damage_dice="1d12", damage_type="Piercing", properties=['Reach', 'Special'])
longsword = Weapon(name="Longsword", damage_dice="1d8", damage_type="Slashing", properties=['Versatile (1d10)'])
maul = Weapon(name="Maul", damage_dice="2d6", damage_type="Bludgeoning", properties=['Heavy', 'Two-Handed'])
morningstar = Weapon(name="Morningstar", damage_dice="1d8", damage_type="Piercing")
pike = Weapon(name="Pike", damage_dice="1d10", damage_type="Piercing", properties=['Heavy', 'Reach', 'Two-Handed'])
rapier = Weapon(name="Rapier", damage_dice="1d8", damage_type="Piercing", properties=['Finesse'])
scimitar = Weapon(name="Scimitar", damage_dice="1d6", damage_type="Slashing", properties=['Finesse', 'Light'])
shortsword = Weapon(name="Shortsword", damage_dice="1d6", damage_type="Piercing", properties=['Finesse', 'Light'])
trident = Weapon(name="Trident", damage_dice="1d6", damage_type="Piercing", properties=['Thrown', 'Versatile (1d8)'])
war_pick = Weapon(name="War Pick", damage_dice="1d8", damage_type="Piercing")
warhammer = Weapon(name="Warhammer", damage_dice="1d8", damage_type="Bludgeoning", properties=['Versatile (1d10)'])
whip = Weapon(name="Whip", damage_dice="1d4", damage_type="Slashing", properties=['Finesse', 'Reach'])

# --- Martial Ranged Weapons ---
blowgun = Weapon(name="Blowgun", damage_dice="1", damage_type="Piercing", properties=['Ammunition', 'Loading'])
hand_crossbow = Weapon(name="Hand Crossbow", damage_dice="1d6", damage_type="Piercing", properties=['Ammunition', 'Light', 'Loading'])
heavy_crossbow = Weapon(name="Heavy Crossbow", damage_dice="1d10", damage_type="Piercing", properties=['Ammunition', 'Heavy', 'Loading', 'Two-Handed'])
longbow = Weapon(name="Longbow", damage_dice="1d8", damage_type="Piercing", properties=['Ammunition', 'Heavy', 'Two-Handed'])
net = Weapon(name="Net", damage_dice="0", damage_type="None", properties=['Special', 'Thrown'])

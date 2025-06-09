import random

def roll_d20(advantage=False, disadvantage=False):
    """
    Rolls a d20, applying advantage or disadvantage.
    Returns the chosen roll and a list of all rolls.
    """
    roll1 = random.randint(1, 20)
    if not (advantage ^ disadvantage):
        return roll1, [roll1]
    roll2 = random.randint(1, 20)
    rolls = sorted([roll1, roll2])
    return (rolls[1], rolls) if advantage else (rolls[0], rolls)

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

# --- NEW: XP and Leveling Data ---
XP_FOR_NEXT_LEVEL = {
    1: 300, 2: 900, 3: 2700, 4: 6500, 5: 14000, 6: 23000, 7: 34000,
    8: 48000, 9: 64000, 10: 85000, 11: 100000, 12: 120000, 13: 140000,
    14: 165000, 15: 195000, 16: 225000, 17: 265000, 18: 305000, 19: 355000, 20: float('inf')
}

XP_FROM_CR = {
    "0": 10, "1/8": 25, "1/4": 50, "1/2": 100, "1": 200, "2": 450, "3": 700,
    "4": 1100, "5": 1800, "6": 2300, "7": 2900, "8": 3900, "9": 5000,
    "10": 5900, "11": 7200, "12": 8400, "13": 10000, "14": 11500, "15": 13000,
    "16": 15000, "17": 18000, "18": 20000, "19": 22000, "20": 25000
}

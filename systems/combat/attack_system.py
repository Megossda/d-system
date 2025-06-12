# File: systems/combat/attack_system.py
"""Global attack system."""

from core import roll_d20, roll, get_ability_modifier

def make_creature_attack(attacker, target, weapon, attack_bonus, action_type="ACTION"):
    """Make a creature attack using global system."""
    
    # Check for advantage conditions
    has_advantage = False
    if hasattr(target, 'is_restrained') and target.is_restrained:
        has_advantage = True
        print(f"** Attack has Advantage (target is Restrained) **")
    
    # Make attack roll
    if has_advantage:
        roll1, _ = roll_d20()
        roll2, _ = roll_d20()
        attack_roll = max(roll1, roll2)
        advantage_text = " (with Advantage)"
    else:
        attack_roll, _ = roll_d20()
        advantage_text = ""
    
    total_attack = attack_roll + attack_bonus
    print(f"ATTACK ROLL: {attack_roll} (1d20{advantage_text}) +{attack_bonus} = {total_attack}")
    
    hit = total_attack >= target.ac or attack_roll == 20
    is_crit = attack_roll == 20
    
    if hit:
        if is_crit:
            print(">>> CRITICAL HIT! <<<")
        else:
            print("The attack hits!")
        
        # Calculate damage
        damage = roll(weapon.damage_dice)
        if is_crit:
            damage += roll(weapon.damage_dice)
        
        str_mod = get_ability_modifier(attacker.stats['str'])
        total_damage = damage + str_mod
        
        print(f"{attacker.name} deals {total_damage} {weapon.damage_type.lower()} damage")
        target.take_damage(total_damage, attacker=attacker)
    else:
        print("The attack misses.")
    
    return {'hit': hit, 'crit': is_crit, 'damage': total_damage if hit else 0}
# File: test_octopus.py
"""
Test script to verify the Giant Octopus works with the Universal Grappling System.
This can be run to test before integrating into the main system.
"""

def test_octopus_grappling():
    """Test the Giant Octopus grappling mechanics."""
    print("=== Testing Giant Octopus with Universal Grappling System ===\n")
    
    # Import what we need
    from enemies.cr_half_1.giant_octopus import GiantOctopus
    from characters.base_character import Character
    from equipment.weapons.martial_melee import longsword
    
    # Create test creatures
    octopus = GiantOctopus("Kraken Jr.", position=0)
    
    # Create a simple test target
    test_fighter = Character(
        name="Test Fighter",
        level=3,
        hp=25,
        stats={'str': 14, 'dex': 12, 'con': 13, 'int': 10, 'wis': 12, 'cha': 10},
        weapon=longsword,
        position=15  # 15 feet away
    )
    
    print("=== Initial State ===")
    print(f"{octopus.name}: {octopus.hp}/{octopus.hp} HP, {len(octopus.grappled_targets)}/{octopus.max_tentacles} tentacles in use")
    print(f"{test_fighter.name}: {test_fighter.hp}/{test_fighter.hp} HP, Grappled: {getattr(test_fighter, 'is_grappled', False)}")
    print(f"Distance: {abs(octopus.position - test_fighter.position)} feet\n")
    
    # Test 1: Octopus tries to attack from too far away
    print("=== Test 1: Attack from long range ===")
    result = octopus.tentacle_attack(test_fighter)
    print(f"Attack result: {result}\n")
    
    # Move octopus closer
    print("=== Moving octopus closer ===")
    octopus.position = 8  # Within 10ft reach
    print(f"New distance: {abs(octopus.position - test_fighter.position)} feet\n")
    
    # Test 2: Successful tentacle attack and grapple
    print("=== Test 2: Tentacle attack in range ===")
    result = octopus.tentacle_attack(test_fighter)
    print(f"Attack result: {result}")
    print(f"Fighter grappled: {getattr(test_fighter, 'is_grappled', False)}")
    print(f"Fighter restrained: {getattr(test_fighter, 'is_restrained', False)}")
    print(f"Octopus grappling targets: {len(octopus.grappled_targets)}\n")
    
    # Test 3: Fighter tries to escape
    print("=== Test 3: Fighter escape attempt ===")
    if hasattr(test_fighter, 'is_grappled') and test_fighter.is_grappled:
        from systems.grappling import UniversalGrappling
        escape_result = UniversalGrappling.attempt_escape(test_fighter, "ACTION")
        print(f"Escape result: {escape_result}")
        print(f"Fighter grappled: {getattr(test_fighter, 'is_grappled', False)}")
        print(f"Fighter restrained: {getattr(test_fighter, 'is_restrained', False)}\n")
    
    # Test 4: Octopus squeezes if still grappling
    print("=== Test 4: Octopus squeeze attack ===")
    if octopus.grappled_targets:
        result = octopus.squeeze_grappled_targets()
        print(f"Squeeze result: {result}")
        print(f"Fighter HP: {test_fighter.hp}/{test_fighter.hp}")
    else:
        print("No grappled targets to squeeze")
    
    print("\n=== Test Complete ===")
    return octopus, test_fighter

def test_octopus_ai():
    """Test the Giant Octopus AI decision making."""
    print("\n=== Testing Giant Octopus AI ===\n")
    
    from enemies.cr_half_1.giant_octopus import GiantOctopus
    from characters.base_character import Character
    from equipment.weapons.martial_melee import longsword
    
    octopus = GiantOctopus("AI Test Octopus", position=0)
    
    # Create multiple test targets
    fighter1 = Character("Fighter 1", 3, 25, 
                        {'str': 14, 'dex': 12, 'con': 13, 'int': 10, 'wis': 12, 'cha': 10},
                        longsword, position=8)
    
    fighter2 = Character("Fighter 2", 3, 25,
                        {'str': 14, 'dex': 12, 'con': 13, 'int': 10, 'wis': 12, 'cha': 10}, 
                        longsword, position=12)
    
    combatants = [octopus, fighter1, fighter2]
    
    print("=== AI Decision Test ===")
    decision = octopus.ai_brain.choose_actions(octopus, combatants)
    print(f"AI chose action: {decision.get('action')}")
    print(f"Target: {decision.get('action_target').name if decision.get('action_target') else 'None'}")
    
    return octopus, fighter1, fighter2

if __name__ == "__main__":
    # Run tests
    octopus, fighter = test_octopus_grappling()
    test_octopus_ai()
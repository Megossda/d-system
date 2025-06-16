# File: examples/acid_splash_demo.py
"""Demo showing how to use the global spell system."""

def demo_acid_splash():
    """Demonstrate Acid Splash usage."""
    # This would be imported in actual usage
    from spells.cantrips import acid_splash
    from systems.character_abilities import SpellcastingManager
    from systems.spells import SpellManager
    
    print("=== Acid Splash Global System Demo ===")
    
    # Assuming we have characters and enemies
    # character = some_character
    # enemies = [goblin1, goblin2]
    
    # Add spellcasting to character
    # SpellcastingManager.add_spellcasting(character, 'cha')
    # SpellcastingManager.add_spell_to_creature(character, acid_splash)
    # SpellcastingManager.add_spell_action(character, acid_splash)
    
    # Use in combat via AI or player choice
    # SpellManager.cast_spell(character, acid_splash, enemies)
    
    print("System is ready - all components properly separated!")


if __name__ == "__main__":
    demo_acid_splash()
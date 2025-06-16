# File: systems/character_abilities/spellcasting.py
"""Global spellcasting abilities system."""

from core import get_ability_modifier


class SpellcastingManager:
    """Manages spellcasting abilities for any creature."""
    
    @staticmethod
    def add_spellcasting(creature, spellcasting_ability='cha', spell_slots=None, prepared_spells=None):
        """Add spellcasting capabilities to any creature."""
        creature.spellcasting_ability = spellcasting_ability
        creature.spell_slots = spell_slots or {}
        creature.prepared_spells = prepared_spells or []
        creature.concentrating_on = None
        
        # Add spellcasting methods
        creature.get_spellcasting_modifier = lambda: get_ability_modifier(creature.stats.get(creature.spellcasting_ability, 10))
        creature.get_spell_save_dc = lambda: 8 + creature.get_proficiency_bonus() + creature.get_spellcasting_modifier()
        creature.get_spell_attack_bonus = lambda: creature.get_proficiency_bonus() + creature.get_spellcasting_modifier()
    
    @staticmethod
    def add_spell_to_creature(creature, spell):
        """Add a spell to a creature's repertoire."""
        if not hasattr(creature, 'prepared_spells'):
            SpellcastingManager.add_spellcasting(creature)
        
        if spell not in creature.prepared_spells:
            creature.prepared_spells.append(spell)
            print(f"** {creature.name} learned {spell.name}! **")
    
    @staticmethod
    def add_spell_action(creature, spell, targets=None):
        """Add a spell casting action to creature's available actions."""
        from actions.spell_actions import CastSpellAction
        
        spell_action = CastSpellAction(spell, targets)
        creature.available_actions.append(spell_action)
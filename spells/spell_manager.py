# File: systems/spells/spell_manager.py
"""Spell Manager - Central hub for all spell operations."""

from core import roll_d20, get_ability_modifier


class SpellManager:
    """Central manager for all spell casting operations."""
    
    @staticmethod
    def cast_spell(caster, spell, targets=None, spell_level=None, action_type="ACTION"):
        """Universal spell casting interface."""
        if not SpellManager._can_cast_spell(caster, spell, spell_level):
            return False
        
        if spell_level is None:
            spell_level = spell.level
        
        # Consume spell slot for non-cantrips
        if spell.level > 0:
            if not SpellManager._consume_spell_slot(caster, spell_level):
                print(f"{caster.name} doesn't have a level {spell_level} spell slot!")
                return False
        
        print(f"{action_type}: {caster.name} casts {spell.name}!")
        return spell.cast(caster, targets, spell_level, action_type)
    
    @staticmethod
    def _can_cast_spell(caster, spell, spell_level):
        """Check if caster can cast the spell."""
        if not hasattr(caster, 'spell_slots'):
            return False
        if hasattr(caster, 'prepared_spells') and spell not in caster.prepared_spells:
            return False
        return True
    
    @staticmethod
    def _consume_spell_slot(caster, spell_level):
        """Consume a spell slot of the given level."""
        if caster.spell_slots.get(spell_level, 0) > 0:
            caster.spell_slots[spell_level] -= 1
            return True
        return False
    
    @staticmethod
    def make_spell_attack(caster, target, spell):
        """Make a spell attack using global systems."""
        from systems.combat.attack_system import make_creature_attack
        
        spell_attack_bonus = caster.get_spellcasting_modifier() + caster.get_proficiency_bonus()
        
        # Create a temporary "spell weapon" for the attack system
        class SpellWeapon:
            def __init__(self, damage_type):
                self.damage_dice = "1d8"  # Default, spells handle their own damage
                self.damage_type = damage_type
        
        spell_weapon = SpellWeapon(spell.damage_type or "Force")
        return make_creature_attack(caster, target, spell_weapon, spell_attack_bonus, "SPELL ATTACK")
    
    @staticmethod
    def make_spell_save(target, caster, spell, save_type):
        """Make a saving throw against a spell."""
        from systems.combat.saving_throws import make_creature_save
        save_dc = caster.get_spell_save_dc()
        return make_creature_save(target, save_type, save_dc)
    
    @staticmethod
    def deal_spell_damage(target, damage, damage_type, caster, is_crit=False):
        """Deal spell damage to a target."""
        if is_crit:
            damage *= 2
            print(f"CRITICAL SPELL DAMAGE: {damage} {damage_type} damage!")
        else:
            print(f"SPELL DAMAGE: {damage} {damage_type} damage")
        target.take_damage(damage, attacker=caster)
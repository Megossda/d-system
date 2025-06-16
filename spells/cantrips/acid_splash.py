# File: spells/cantrips/acid_splash.py
"""Acid Splash cantrip."""

from ..base_spell import BaseSpell
from core import roll


class AcidSplash(BaseSpell):
    """Acid Splash cantrip."""
    
    def __init__(self):
        super().__init__(
            name="Acid Splash",
            level=0,
            school="Evocation",
            damage_type="Acid",
            save_type="dex"
        )
    
    def cast(self, caster, targets, spell_level, action_type="ACTION"):
        """Cast Acid Splash."""
        from systems.spells import SpellManager
        
        if not targets:
            print(f"** {self.name} requires a target point! **")
            return False
        
        if not isinstance(targets, list):
            targets = [targets]
        
        damage_dice = self._get_cantrip_damage_dice(caster.level)
        
        print(f"** Acidic bubble explodes in a 5-foot-radius sphere! **")
        
        for target in targets:
            if not target or not target.is_alive:
                continue
            
            print(f"--- {target.name} makes a Dexterity saving throw ---")
            
            if SpellManager.make_spell_save(target, caster, self, "dex"):
                print(f"** {target.name} succeeds and takes no damage! **")
            else:
                total_damage = 0
                for _ in range(damage_dice):
                    total_damage += roll("1d6")
                
                print(f"** {target.name} fails and takes {total_damage} acid damage! **")
                SpellManager.deal_spell_damage(target, total_damage, "Acid", caster)
        
        return True
    
    def _get_cantrip_damage_dice(self, caster_level):
        """Cantrip scaling."""
        if caster_level >= 17:
            return 4
        elif caster_level >= 11:
            return 3
        elif caster_level >= 5:
            return 2
        else:
            return 1


# Create the instance
acid_splash = AcidSplash()
from .base_actions import Action


class CastSpellAction(Action):
    def __init__(self, spell):  # FIXED: was def **init**
        super().__init__(f"Cast {spell.name}")
        self.spell = spell

    def execute(self, performer, target=None, action_type="ACTION"):
        """Executes the spell cast, including spending the slot."""  # FIXED: was *"""
        if performer.spell_slots.get(self.spell.level, 0) > 0:
            log_message = f"{action_type}: {performer.name} expends a level {self.spell.level} spell slot ({performer.spell_slots[self.spell.level] - 1} remaining), to cast {self.spell.name} ({self.spell.school})"
            if "Ranged" in self.spell.attack_save or "Melee" in self.spell.attack_save:
                if target:
                    log_message += f" at {target.name} (AC: {target.ac})."
            else:
                log_message += "."
            print(log_message)
            performer.spell_slots[self.spell.level] -= 1
            performer.cast_spell(self.spell, target, action_type)
        else:
            print(
                f"{action_type}: {performer.name} tries to cast {self.spell.name} but is out of level {self.spell.level} slots!")
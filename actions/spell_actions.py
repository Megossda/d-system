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


# File: actions/special_actions.py (ADD new escape action)
class EscapeGrappleAction(Action):
    """Action to escape from a grapple using Athletics or Acrobatics."""

    def __init__(self):
        super().__init__("Escape Grapple")

    def execute(self, performer, target=None, action_type="ACTION"):
        if not hasattr(performer, 'is_grappled') or not performer.is_grappled:
            print(f"{action_type}: {performer.name} is not grappled!")
            return

        # Find the grappler
        grappler = None
        for other in performer.current_combatants:  # We'll need to pass this
            if (hasattr(other, 'is_grappling') and other.is_grappling and
                    hasattr(other, 'grapple_target') and other.grapple_target == performer):
                grappler = other
                break

        if not grappler:
            print(f"{action_type}: {performer.name} cannot find their grappler!")
            return

        performer.attempt_grapple_escape(grappler, action_type)
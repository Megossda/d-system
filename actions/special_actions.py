from .base_actions import Action
from core import get_ability_modifier, roll_d20  # FIXED: Added missing imports


class LayOnHandsAction(Action):
    """Represents the Paladin's Lay on Hands ability."""

    def __init__(self):
        super().__init__("Lay on Hands")

    def execute(self, performer, target=None, action_type="BONUS ACTION"):
        target_to_heal = target or performer
        heal_amount = performer.get_optimal_lay_on_hands_amount(target_to_heal)
        performer.use_lay_on_hands(heal_amount, target_to_heal)


class MultiattackAction(Action):
    """An action that represents a creature's multiattack."""

    def __init__(self, creature):
        super().__init__("Multiattack")
        self.creature = creature
        # FIXED: Store the creature reference for movement calculations
        self.action = self  # For compatibility with movement detection

    def execute(self, performer, target, action_type="ACTION"):
        if hasattr(performer, 'multiattack'):
            performer.multiattack(target, action_type)
        else:
            performer.attack(target, action_type)


class EscapeGrappleAction(Action):
    """Action to escape from a grapple using Athletics or Acrobatics - PHB 2024."""

    def __init__(self):
        super().__init__("Escape Grapple")

    def execute(self, performer, target=None, action_type="ACTION"):
        # FIXED: Check grappled status properly
        if not hasattr(performer, 'is_grappled') or not performer.is_grappled:
            print(f"{action_type}: {performer.name} is not grappled!")
            return

        # FIXED: Use stored grappler reference
        if not hasattr(performer, 'grappler') or not performer.grappler:
            print(f"{action_type}: {performer.name} has no grappler reference!")
            return

        grappler = performer.grappler
        
        # Verify grappler is still alive and grappling
        if not grappler.is_alive:
            print(f"{action_type}: {performer.name}'s grappler is dead, automatically freed!")
            self._free_from_grapple(performer, grappler)
            return

        if not hasattr(grappler, 'is_grappling') or not grappler.is_grappling:
            print(f"{action_type}: {performer.name}'s grappler is no longer grappling, automatically freed!")
            self._free_from_grapple(performer, grappler)
            return

        # FIXED: PHB 2024 escape attempt
        self._attempt_escape(performer, grappler, action_type)

    def _attempt_escape(self, performer, grappler, action_type):
        """Attempt to escape using Athletics or Acrobatics vs escape DC."""
        print(f"--- {performer.name} attempts to break free from {grappler.name}'s grapple! ---")

        # Choose between Athletics (STR) or Acrobatics (DEX)
        athletics_mod = get_ability_modifier(performer.stats['str'])
        acrobatics_mod = get_ability_modifier(performer.stats['dex'])

        # Add proficiency if character has it
        if 'Athletics' in getattr(performer, 'skill_proficiencies', []):
            athletics_mod += performer.get_proficiency_bonus()
            athletics_has_prof = True
        else:
            athletics_has_prof = False

        if 'Acrobatics' in getattr(performer, 'skill_proficiencies', []):
            acrobatics_mod += performer.get_proficiency_bonus()
            acrobatics_has_prof = True
        else:
            acrobatics_has_prof = False

        # Choose the better option
        if athletics_mod >= acrobatics_mod:
            chosen_skill = "Athletics"
            my_modifier = athletics_mod
            ability = "STR"
            base_mod = get_ability_modifier(performer.stats['str'])
            prof_text = f" +{performer.get_proficiency_bonus()} (Prof)" if athletics_has_prof else ""
        else:
            chosen_skill = "Acrobatics"
            my_modifier = acrobatics_mod
            ability = "DEX"
            base_mod = get_ability_modifier(performer.stats['dex'])
            prof_text = f" +{performer.get_proficiency_bonus()} (Prof)" if acrobatics_has_prof else ""

        # Make the escape attempt
        escape_roll, _ = roll_d20()
        my_total = escape_roll + my_modifier

        # Get escape DC (should be stored from when grapple was applied)
        escape_dc = getattr(performer, 'grapple_escape_dc', 8 + get_ability_modifier(grappler.stats['str']) + grappler.get_proficiency_bonus())

        print(f"{action_type}: {performer.name} ({chosen_skill}): {escape_roll} (1d20) +{base_mod} ({ability}){prof_text} = {my_total}")
        print(f"Escape DC: {escape_dc}")

        if my_total >= escape_dc:
            print(f"** {performer.name} breaks free from the grapple! **")
            self._free_from_grapple(performer, grappler)
        else:
            print(f"** {performer.name} fails to break free and remains grappled! **")

    def _free_from_grapple(self, performer, grappler):
        """Free the performer from grapple and clean up state."""
        # Clear grappled state
        performer.is_grappled = False
        if hasattr(performer, 'grappler'):
            delattr(performer, 'grappler')
        if hasattr(performer, 'grapple_escape_dc'):
            delattr(performer, 'grapple_escape_dc')

        # Clear grappling state
        if hasattr(grappler, 'is_grappling'):
            grappler.is_grappling = False
        if hasattr(grappler, 'grapple_target'):
            grappler.grapple_target = None

        print(f"** {performer.name} is no longer grappled! **")
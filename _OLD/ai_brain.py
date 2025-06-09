from actions import AttackAction, CastSpellAction, LayOnHandsAction
from spells.level_1 import searing_smite, guiding_bolt, cure_wounds


class AIBrain:
    """A base class for character decision-making AI."""

    def choose_actions(self, character, combatants):
        """
        Determines the best action and bonus action for a character to take.
        Returns a dictionary with action, bonus_action, and targets.
        """
        action = AttackAction(character.equipped_weapon)
        bonus_action = None
        target = next((c for c in combatants if c.is_alive and c != character), None)

        return {
            'action': action,
            'bonus_action': bonus_action,
            'action_target': target,
            'bonus_action_target': None
        }


class PaladinAIBrain(AIBrain):
    """Advanced Paladin AI with intelligent healing system that follows 2024 spell slot rules."""

    def choose_actions(self, character, combatants):
        """
        Advanced AI Logic with Healing System:
        1. Assess healing needs (self and allies)
        2. Choose optimal healing method (Lay on Hands vs Cure Wounds)
        3. Balance offense vs healing based on threat level
        4. Follow 2024 spell slot rules (only one spell slot per turn)
        """
        action = None
        bonus_action = None
        action_target = next((c for c in combatants if c.is_alive and c != character), None)
        bonus_action_target = None
        used_spell_slot = False

        # --- HEALING ASSESSMENT ---
        healing_priority = self._assess_healing_priority(character, combatants)

        # --- DECISION TREE ---
        if healing_priority['critical_healing_needed']:
            # CRITICAL: Use best available healing immediately
            if healing_priority['use_cure_wounds']:
                # Use Cure Wounds (action)
                cure_action = self._get_cure_wounds_action(character)
                if cure_action:
                    action = cure_action
                    action_target = healing_priority['heal_target']
                    used_spell_slot = True
                    print(f"[HEALING AI] {character.name}: Critical healing needed! Using Cure Wounds.")
            elif healing_priority['use_lay_on_hands']:
                # Use Lay on Hands (bonus action)
                loh_action = self._get_lay_on_hands_action(character)
                if loh_action:
                    bonus_action = loh_action
                    bonus_action_target = healing_priority['heal_target']
                    print(f"[HEALING AI] {character.name}: Critical healing needed! Using Lay on Hands.")

        elif healing_priority['moderate_healing_needed']:
            # MODERATE: Consider healing as bonus action
            if healing_priority['use_lay_on_hands']:
                loh_action = self._get_lay_on_hands_action(character)
                if loh_action:
                    bonus_action = loh_action
                    bonus_action_target = healing_priority['heal_target']
                    print(f"[HEALING AI] {character.name}: Moderate healing needed, using Lay on Hands.")

        # --- OFFENSIVE ACTIONS ---
        # Choose offensive action if not healing or if bonus action healing
        if not action:
            # Priority 1: Cast offensive spells if we have slots and haven't used one
            if not used_spell_slot and character.spell_slots.get(1, 0) > 0:
                gb_action = self._get_guiding_bolt_action(character)
                if gb_action and action_target:
                    action = gb_action
                    used_spell_slot = True

            # Default to weapon attack
            if not action:
                action = AttackAction(character.equipped_weapon)

        # --- OFFENSIVE BONUS ACTIONS ---
        # Use Searing Smite if no healing bonus action and no spell slot used
        if (not bonus_action and not character.concentrating_on and
                not used_spell_slot and character.spell_slots.get(1, 0) > 0):
            smite_action = self._get_searing_smite_action(character)
            if smite_action:
                bonus_action = smite_action
                bonus_action_target = action_target
                used_spell_slot = True

        return {
            'action': action,
            'bonus_action': bonus_action,
            'action_target': action_target,
            'bonus_action_target': bonus_action_target
        }

    def _assess_healing_priority(self, character, combatants):
        """Assess healing needs and determine optimal healing strategy"""
        allies = [c for c in combatants if c.is_alive and c != character and hasattr(c, 'spell_slots')]
        heal_target = character  # Default to self-healing

        # Find most injured ally (including self)
        all_possible_targets = [character] + allies
        most_injured = min(all_possible_targets, key=lambda c: c.hp / c.max_hp)

        heal_target = most_injured
        hp_percent = heal_target.hp / heal_target.max_hp

        # Determine healing urgency
        critical_healing = hp_percent <= 0.25  # 25% or less HP
        moderate_healing = hp_percent <= 0.50  # 50% or less HP

        # Available healing options
        has_cure_wounds = (character.spell_slots.get(1, 0) > 0 and
                           cure_wounds in getattr(character, 'prepared_spells', []))
        has_lay_on_hands = character.lay_on_hands_pool > 0

        # Healing strategy logic
        use_cure_wounds = False
        use_lay_on_hands = False

        if critical_healing:
            if has_cure_wounds:
                # Cure Wounds heals more on average (1d8+mod vs flat 10 from LoH)
                cure_avg = 4.5 + character.get_spellcasting_modifier()  # ~6-7 HP
                loh_heal = min(10, character.lay_on_hands_pool)
                if cure_avg >= loh_heal or character.lay_on_hands_pool < 5:
                    use_cure_wounds = True
                else:
                    use_lay_on_hands = True
            elif has_lay_on_hands:
                use_lay_on_hands = True

        elif moderate_healing:
            # For moderate healing, prefer Lay on Hands to save spell slots
            if has_lay_on_hands:
                use_lay_on_hands = True
            elif has_cure_wounds:
                use_cure_wounds = True

        return {
            'critical_healing_needed': critical_healing,
            'moderate_healing_needed': moderate_healing,
            'heal_target': heal_target,
            'use_cure_wounds': use_cure_wounds,
            'use_lay_on_hands': use_lay_on_hands,
            'target_hp_percent': hp_percent
        }

    def _get_cure_wounds_action(self, character):
        """Get Cure Wounds action if available"""
        return next((a for a in character.available_actions if a.name == "Cast Cure Wounds"), None)

    def _get_lay_on_hands_action(self, character):
        """Get Lay on Hands action if available"""
        return next((ba for ba in character.available_bonus_actions if isinstance(ba, LayOnHandsAction)), None)

    def _get_guiding_bolt_action(self, character):
        """Get Guiding Bolt action if available"""
        return next((a for a in character.available_actions if a.name == "Cast Guiding Bolt"), None)

    def _get_searing_smite_action(self, character):
        """Get Searing Smite action if available"""
        return next((ba for ba in character.available_bonus_actions if ba.name == "Cast Searing Smite"), None)


class HobgoblinWarriorAIBrain(AIBrain):
    """AI for the Hobgoblin Warrior to choose between melee and ranged attacks."""

    def choose_actions(self, character, combatants):
        action = None
        target = next((c for c in combatants if c.is_alive and c != character), None)

        if target:
            distance = abs(character.position - target.position)
            # If target is far away, use the longbow
            if distance > 5 and character.secondary_weapon:
                action = AttackAction(character.secondary_weapon)
            # Otherwise, use the longsword
            else:
                action = AttackAction(character.equipped_weapon)
        else:
            action = AttackAction(character.equipped_weapon)

        return {'action': action, 'bonus_action': None, 'action_target': target}
# File: ai/character_ai/paladin_ai.py
from ..base_ai import AIBrain
from actions.base_actions import AttackAction
from actions.spell_actions import CastSpellAction
from actions.special_actions import LayOnHandsAction, EscapeGrappleAction

class PaladinAIBrain(AIBrain):
    """Advanced Paladin AI with intelligent healing system and spell slot conservation."""

    def choose_actions(self, character, combatants):
        """
        Advanced AI Logic with Spell Slot Conservation and Grapple Handling:
        1. Handle grappled condition (escape vs fight) - PRIORITY 1
        2. Assess healing needs and spell slot availability
        3. Conserve spell slots for emergency healing
        4. Choose optimal healing method (Lay on Hands vs Cure Wounds)
        5. Consider tactical retreat when badly wounded
        6. Balance offense vs healing based on threat level and resources
        """
        action = None
        bonus_action = None
        action_target = next((c for c in combatants if c.is_alive and c != character), None)
        bonus_action_target = None
        used_spell_slot = False

        # --- SPELL SLOT CONSERVATION ASSESSMENT ---
        resource_status = self._assess_spell_slot_conservation(character)

        # --- GRAPPLE HANDLING (HIGHEST PRIORITY) ---
        grapple_decision = self._assess_grapple_situation(character, action_target)
        
        # --- HEALING ASSESSMENT ---
        healing_priority = self._assess_healing_priority(character, combatants, resource_status)

        # --- TACTICAL RETREAT ASSESSMENT (only if not grappled) ---
        retreat_decision = {'should_retreat': False}
        if not character.is_grappled:
            retreat_decision = self._assess_tactical_retreat(character, action_target)

        # --- DECISION TREE ---
        
        # PRIORITY 1: Handle grapple situation (ABSOLUTE PRIORITY)
        if grapple_decision['should_escape']:
            action = EscapeGrappleAction()
            print(f"[GRAPPLE AI] {character.name}: {grapple_decision['reason']}")
            
            # Set flag to prevent tactical AI override
            character._ai_has_made_critical_decision = True
            character._critical_decision_reason = "Grapple escape takes absolute priority"
        
        # PRIORITY 2: Critical healing (only if not escaping grapple)
        elif healing_priority['critical_healing_needed']:
            if healing_priority['use_cure_wounds']:
                # Use Cure Wounds (action)
                cure_action = self._get_cure_wounds_action(character)
                if cure_action:
                    action = cure_action
                    action_target = healing_priority['heal_target']
                    used_spell_slot = True
                    character._ai_has_made_critical_decision = True
                    character._critical_decision_reason = "Critical healing takes priority"
                    print(f"[HEALING AI] {character.name}: Critical healing! Using Cure Wounds (2d8+2 = ~11 HP).")
            elif healing_priority['use_lay_on_hands']:
                # Use Lay on Hands (bonus action)
                loh_action = self._get_lay_on_hands_action(character)
                if loh_action:
                    bonus_action = loh_action
                    bonus_action_target = healing_priority['heal_target']
                    print(f"[HEALING AI] {character.name}: Critical healing! Using Lay on Hands.")

        # PRIORITY 3: Moderate healing (only as bonus action)
        if healing_priority['moderate_healing_needed'] and not bonus_action:
            if healing_priority['use_lay_on_hands']:
                loh_action = self._get_lay_on_hands_action(character)
                if loh_action:
                    bonus_action = loh_action
                    bonus_action_target = healing_priority['heal_target']
                    print(f"[HEALING AI] {character.name}: Moderate healing, using Lay on Hands.")

        # PRIORITY 4: Tactical retreat logic (only if not grappled and no action chosen)
        if retreat_decision['should_retreat'] and not action and not resource_status['conserve_slots']:
            # Only retreat with spells if we're not conserving slots
            if not used_spell_slot and character.spell_slots.get(1, 0) > 0:
                gb_action = self._get_guiding_bolt_action(character)
                if gb_action and action_target:
                    action = gb_action
                    used_spell_slot = True
                    character._ai_has_made_critical_decision = True
                    character._critical_decision_reason = "Tactical retreat with ranged attack"
                    print(f"[TACTICAL AI] {character.name}: Retreating and using ranged attack!")
            
            # If conserving slots or no ranged spell, just retreat
            if not action:
                action = AttackAction(character.equipped_weapon)
                character._ai_has_made_critical_decision = True
                character._critical_decision_reason = "Tactical retreat movement"
                print(f"[TACTICAL AI] {character.name}: Retreating to safer distance!")

        # PRIORITY 5: Offensive actions
        if not action:
            # Calculate distance to target for tactical decisions
            distance_to_target = abs(character.position - action_target.position) if action_target else 999
            
            # Only use offensive spells if NOT conserving slots
            if (not used_spell_slot and character.spell_slots.get(1, 0) > 0 and 
                not resource_status['conserve_slots']):
                
                # Use Guiding Bolt if target is far away (better than moving into melee)
                if distance_to_target > 10:
                    gb_action = self._get_guiding_bolt_action(character)
                    if gb_action and action_target:
                        action = gb_action
                        used_spell_slot = True
                        print(f"[TACTICAL AI] {character.name}: Target far away, using ranged spell!")

            # Default to weapon attack - but control Divine Smite based on conservation
            if not action:
                # Create attack action that respects slot conservation
                attack_action = AttackAction(character.equipped_weapon)
                
                # Set Divine Smite allowance based on conservation status
                if resource_status['conserve_slots']:
                    # Store conservation status so attack method can check it
                    character._conserving_slots_for_healing = True
                    print(f"[AI CONTROL] {character.name}: Attack without Divine Smite (conserving slots)")
                else:
                    character._conserving_slots_for_healing = False
                    
                action = attack_action

        # --- OFFENSIVE BONUS ACTIONS ---
        # FIXED: Only use Searing Smite if target doesn't already have it
        if (not bonus_action and not character.concentrating_on and
                not used_spell_slot and character.spell_slots.get(1, 0) > 0 and
                not resource_status['conserve_slots']):
            
            # Check if target already has Searing Smite
            target_has_searing_smite = False
            if action_target and hasattr(action_target, 'searing_smite_effect'):
                target_has_searing_smite = action_target.searing_smite_effect.get('active', False)
            
            # Only use Searing Smite if target doesn't have it and we're planning melee attacks
            if not target_has_searing_smite and isinstance(action, AttackAction):
                smite_action = self._get_searing_smite_action(character)
                if smite_action:
                    bonus_action = smite_action
                    bonus_action_target = action_target
                    used_spell_slot = True
                    print(f"[AI CONTROL] {character.name}: Using Searing Smite on fresh target")
            elif target_has_searing_smite:
                print(f"[AI CONTROL] {character.name}: Target already has Searing Smite, skipping duplicate")

        return {
            'action': action,
            'bonus_action': bonus_action,
            'action_target': action_target,
            'bonus_action_target': bonus_action_target
        }

    def _assess_spell_slot_conservation(self, character):
        """Assess whether to conserve spell slots for emergency healing."""
        total_slots = sum(character.spell_slots.values())
        our_hp_percent = character.hp / character.max_hp
        
        # Check if we have Cure Wounds prepared
        from spells.level_1.cure_wounds import cure_wounds
        has_cure_wounds_prepared = cure_wounds in getattr(character, 'prepared_spells', [])
        
        # Conservation rules:
        # 1. If we have ≤1 spell slot and Cure Wounds prepared, ALWAYS conserve
        # 2. If HP ≤ 60% and ≤2 slots, conserve one for healing
        # 3. If HP ≤ 40%, conserve at least one slot regardless (lowered from 35% for better healing)
        
        conserve_slots = False
        reason = ""
        
        if total_slots <= 1 and has_cure_wounds_prepared:
            conserve_slots = True
            reason = f"Only {total_slots} slot(s) left, conserving for Cure Wounds"
        elif our_hp_percent <= 0.40 and total_slots >= 1 and has_cure_wounds_prepared:
            conserve_slots = True
            reason = f"Moderate HP ({our_hp_percent:.1%}), conserving slot for Cure Wounds"
        elif our_hp_percent <= 0.60 and total_slots <= 2 and has_cure_wounds_prepared:
            conserve_slots = True
            reason = f"Lower HP ({our_hp_percent:.1%}) with only {total_slots} slots, conserving for healing"
        
        if conserve_slots:
            print(f"[RESOURCE AI] {character.name}: {reason}")
        
        return {
            'conserve_slots': conserve_slots,
            'reason': reason,
            'total_slots': total_slots,
            'has_cure_wounds_prepared': has_cure_wounds_prepared
        }

    def _assess_grapple_situation(self, character, target):
        """Assess whether to escape grapple or fight while grappled."""
        if not hasattr(character, 'is_grappled') or not character.is_grappled:
            return {'should_escape': False, 'reason': 'Not grappled'}
        
        our_hp_percent = character.hp / character.max_hp
        
        # Decision factors for escaping grapple
        should_escape = False
        reason = ""
        
        # FIXED: More aggressive grapple escape logic
        # ALWAYS try to escape if wounded (≤75% HP) - grappling is very dangerous
        if our_hp_percent <= 0.75:
            should_escape = True
            reason = f"Wounded while grappled ({our_hp_percent:.1%} HP), must escape dangerous situation!"
        
        # Even if healthy, consider escape chance vs attack disadvantage
        elif our_hp_percent > 0.75:
            # Calculate escape chance
            athletics_mod = get_ability_modifier(character.stats['str'])
            if 'Athletics' in getattr(character, 'skill_proficiencies', []):
                athletics_mod += character.get_proficiency_bonus()
            
            escape_dc = getattr(character, 'grapple_escape_dc', 15)
            escape_chance = ((21 + athletics_mod - escape_dc) / 20.0) * 100
            
            # If we have good escape chance (≥60%), try it
            if escape_chance >= 60:
                should_escape = True
                reason = f"Good escape chance ({escape_chance:.0f}%), better than attacking with disadvantage"
            else:
                reason = f"Poor escape chance ({escape_chance:.0f}%), fighting while grappled"
        
        return {
            'should_escape': should_escape,
            'reason': reason
        }

    def _assess_healing_priority(self, character, combatants, resource_status):
        """Assess healing needs and determine optimal healing strategy with proper slot checking."""
        allies = [c for c in combatants if c.is_alive and c != character and hasattr(c, 'spell_slots')]
        heal_target = character  # Default to self-healing

        # Find most injured ally (including self)
        all_possible_targets = [character] + allies
        most_injured = min(all_possible_targets, key=lambda c: c.hp / c.max_hp)

        heal_target = most_injured
        hp_percent = heal_target.hp / heal_target.max_hp

        # FIXED: More aggressive healing thresholds for grappled situations
        if hasattr(character, 'is_grappled') and character.is_grappled:
            # More aggressive when grappled (taking crush damage each turn)
            critical_healing = hp_percent <= 0.50  # 50% when grappled
            moderate_healing = hp_percent <= 0.70  # 70% when grappled
        else:
            # Normal thresholds when not grappled
            critical_healing = hp_percent <= 0.40  # 40% or less HP (was 35%)
            moderate_healing = hp_percent <= 0.65  # 65% or less HP (was 60%)

        # FIXED: Proper Cure Wounds availability check
        from spells.level_1.cure_wounds import cure_wounds
        cure_wounds_prepared = cure_wounds in getattr(character, 'prepared_spells', [])
        has_cure_wounds_slots = character.spell_slots.get(1, 0) > 0
        
        # Check if we can actually use Cure Wounds (prepared AND have slots)
        has_cure_wounds = cure_wounds_prepared and has_cure_wounds_slots
        has_lay_on_hands = character.lay_on_hands_pool > 0

        # Log for debugging
        print(f"[HEALING DEBUG] HP: {character.hp}/{character.max_hp} ({hp_percent:.1%})")
        print(f"[HEALING DEBUG] Cure Wounds available: {has_cure_wounds} (prep: {cure_wounds_prepared}, slots: {has_cure_wounds_slots})")
        print(f"[HEALING DEBUG] Lay on Hands pool: {character.lay_on_hands_pool}")

        # Healing strategy logic with CORRECTED availability checking
        use_cure_wounds = False
        use_lay_on_hands = False

        if critical_healing:
            if has_cure_wounds:
                # FIXED: Cure Wounds heals 2d8+mod (PHB 2024), much better than Lay on Hands
                cure_avg = 9.0 + character.get_spellcasting_modifier()  # 2d8 = 9 average, +2 CHA = ~11 HP
                loh_heal = min(character.lay_on_hands_pool, 15)  # Use more LoH for critical situations
                
                # ALWAYS prefer Cure Wounds for critical healing (better healing + more efficient)
                use_cure_wounds = True
                print(f"[HEALING AI] Critical healing: Cure Wounds (~{cure_avg:.1f} HP) vs Lay on Hands ({loh_heal} HP) - choosing Cure Wounds")
            elif has_lay_on_hands:
                use_lay_on_hands = True
                print(f"[HEALING AI] Critical healing: No Cure Wounds available, using Lay on Hands")

        elif moderate_healing:
            # For moderate healing, still prefer Cure Wounds if not conserving slots
            if has_cure_wounds and not resource_status['conserve_slots']:
                use_cure_wounds = True
                print(f"[HEALING AI] Moderate healing: Using Cure Wounds (slots available and not conserving)")
            elif has_lay_on_hands:
                use_lay_on_hands = True
                print(f"[HEALING AI] Moderate healing: Using Lay on Hands (conserving slots or no Cure Wounds)")

        return {
            'critical_healing_needed': critical_healing,
            'moderate_healing_needed': moderate_healing,
            'heal_target': heal_target,
            'use_cure_wounds': use_cure_wounds,
            'use_lay_on_hands': use_lay_on_hands,
            'target_hp_percent': hp_percent
        }

    def _assess_tactical_retreat(self, character, target):
        """Assess whether the paladin should retreat to use ranged attacks."""
        if not target:
            return {'should_retreat': False, 'reason': 'No target'}
        
        our_hp_percent = character.hp / character.max_hp
        current_distance = abs(character.position - target.position)
        
        # Consider retreat if badly wounded and have ranged options
        should_retreat = False
        reason = ""
        
        # Check if we have Guiding Bolt available
        from spells.level_1.guiding_bolt import guiding_bolt
        has_guiding_bolt = (character.spell_slots.get(1, 0) > 0 and
                           guiding_bolt in getattr(character, 'prepared_spells', []))
        
        if our_hp_percent <= 0.40 and has_guiding_bolt:  # 40% HP or less
            if current_distance <= 10:  # Currently in or near melee range
                should_retreat = True
                reason = f"Low HP ({our_hp_percent:.1%}), retreating to use ranged attacks"
                print(f"[TACTICAL AI] {reason}")
        
        return {
            'should_retreat': should_retreat,
            'reason': reason,
            'has_ranged_options': has_guiding_bolt
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
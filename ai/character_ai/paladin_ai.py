# File: ai/character_ai/paladin_ai.py
from ..base_ai import AIBrain
from actions.base_actions import AttackAction
from actions.spell_actions import CastSpellAction
from actions.special_actions import LayOnHandsAction, EscapeGrappleAction  # ADD EscapeGrappleAction here

class PaladinAIBrain(AIBrain):
    """Advanced Paladin AI with intelligent healing system and spell slot conservation."""

    def choose_actions(self, character, combatants):
        """
        Enhanced AI Logic with Critical Situation Handling:
        1. CRITICAL SURVIVAL: Life-threatening situations override all other priorities
        2. Handle grappled condition (escape vs fight vs heal) - CONTEXT-DEPENDENT
        3. Assess healing needs and spell slot availability
        4. Conserve spell slots for emergency healing (with survival exceptions)
        5. Choose optimal healing method (Lay on Hands vs Cure Wounds)
        6. Consider tactical retreat when badly wounded
        7. Balance offense vs healing based on threat level and resources
        """
        action = None
        bonus_action = None
        action_target = next((c for c in combatants if c.is_alive and c != character), None)  # Default target
        bonus_action_target = None
        used_spell_slot = False

        # --- CRITICAL SURVIVAL ASSESSMENT ---
        survival_status = self._assess_critical_survival(character, action_target)

        # --- SPELL SLOT CONSERVATION ASSESSMENT ---
        resource_status = self._assess_spell_slot_conservation(character, survival_override=survival_status['override_conservation'])

        # --- GRAPPLE HANDLING (CONTEXT-DEPENDENT PRIORITY) ---
        grapple_decision = self._assess_grapple_situation(character, action_target, survival_status)
        
        # --- HEALING ASSESSMENT ---
        healing_priority = self._assess_healing_priority(character, combatants, resource_status, survival_status)

        # --- CHANNEL DIVINITY ASSESSMENT ---
        channel_divinity_decision = self._assess_channel_divinity_usage(character, grapple_decision)
        
        # Use Channel Divinity if beneficial (as bonus action)
        if channel_divinity_decision['should_use'] and not bonus_action:
            if channel_divinity_decision['option'] == 'Peerless Athlete':
                # Set up to use Peerless Athlete
                character._use_peerless_athlete = True
                print(f"[CHANNEL DIVINITY] {character.name}: {channel_divinity_decision['reason']}")

        # --- TACTICAL RETREAT ASSESSMENT (only if not grappled) ---
        retreat_decision = {'should_retreat': False}
        if not character.is_grappled:
            retreat_decision = self._assess_tactical_retreat(character, action_target)

        # --- ENHANCED DECISION TREE ---
        
        # PRIORITY 1: CRITICAL SURVIVAL - Life-threatening healing (ABSOLUTE PRIORITY)
        if survival_status['needs_emergency_healing']:
            if healing_priority['use_cure_wounds']:
                cure_action = self._get_cure_wounds_action(character)
                if cure_action:
                    action = cure_action
                    action_target = healing_priority['heal_target']
                    used_spell_slot = True
                    character._ai_has_made_critical_decision = True
                    character._critical_decision_reason = "EMERGENCY HEALING - Life-threatening situation"
                    print(f"[EMERGENCY AI] {character.name}: CRITICAL SURVIVAL - Using emergency Cure Wounds!")
            elif healing_priority['use_lay_on_hands']:
                loh_action = self._get_lay_on_hands_action(character)
                if loh_action:
                    # FIXED: For emergency, use Lay on Hands as ACTION, not bonus action
                    action = loh_action  # This uses the ACTION slot
                    action_target = healing_priority['heal_target']
                    character._ai_has_made_critical_decision = True
                    character._critical_decision_reason = "EMERGENCY HEALING - Using Lay on Hands as action"
                    print(f"[EMERGENCY AI] {character.name}: CRITICAL SURVIVAL - Using emergency Lay on Hands as ACTION!")
            
            # SAFETY CHECK: Ensure we have valid targets for emergency healing
            if not action_target:
                action_target = character  # Default to self-healing

        # PRIORITY 2: Handle grapple situation (ONLY if not in critical survival mode)
        elif grapple_decision['should_escape']:
            action = EscapeGrappleAction()
            print(f"[GRAPPLE AI] {character.name}: {grapple_decision['reason']}")
            
            character._ai_has_made_critical_decision = True
            character._critical_decision_reason = "Grapple escape takes priority"
        
        # PRIORITY 3: Critical healing (only if not escaping grapple or in emergency)
        elif healing_priority['critical_healing_needed']:
            if healing_priority['use_cure_wounds']:
                cure_action = self._get_cure_wounds_action(character)
                if cure_action:
                    action = cure_action
                    action_target = healing_priority['heal_target']
                    used_spell_slot = True
                    character._ai_has_made_critical_decision = True
                    character._critical_decision_reason = "Critical healing takes priority"
                    print(f"[HEALING AI] {character.name}: Critical healing! Using Cure Wounds (~11.0 HP).")
            elif healing_priority['use_lay_on_hands']:
                loh_action = self._get_lay_on_hands_action(character)
                if loh_action:
                    bonus_action = loh_action
                    bonus_action_target = healing_priority['heal_target']
                    print(f"[HEALING AI] {character.name}: Critical healing! Using Lay on Hands.")

        # PRIORITY 4: Moderate healing (only as bonus action)
                if healing_priority['moderate_healing_needed'] and not bonus_action:
                    if healing_priority['use_lay_on_hands']:
                        loh_action = self._get_lay_on_hands_action(character)
                        if loh_action:
                            bonus_action = loh_action
                            bonus_action_target = healing_priority['heal_target']
                            print(f"[HEALING AI] {character.name}: Moderate healing, using Lay on Hands.")

        # PRIORITY 4.5: Channel Divinity usage (Peerless Athlete)
        if hasattr(character, '_use_peerless_athlete') and character._use_peerless_athlete and not bonus_action:
                    # Use Peerless Athlete - call it directly and mark bonus action as used
                    if character.use_peerless_athlete():
                        character._use_peerless_athlete = False
                        print(f"[CHANNEL DIVINITY] {character.name}: Used Peerless Athlete for grapple escape advantage!")

        # PRIORITY 5: Tactical retreat logic (only if not grappled and no action chosen)
        if retreat_decision['should_retreat'] and not action and not resource_status['conserve_slots']:
            if not used_spell_slot and character.spell_slots.get(1, 0) > 0:
                gb_action = self._get_guiding_bolt_action(character)
                if gb_action and action_target:
                    action = gb_action
                    used_spell_slot = True
                    character._ai_has_made_critical_decision = True
                    character._critical_decision_reason = "Tactical retreat with ranged attack"
                    print(f"[TACTICAL AI] {character.name}: Retreating and using ranged attack!")
            
            if not action:
                action = AttackAction(character.equipped_weapon)
                character._ai_has_made_critical_decision = True
                character._critical_decision_reason = "Tactical retreat movement"
                print(f"[TACTICAL AI] {character.name}: Retreating to safer distance!")

        # PRIORITY 6: Offensive actions
        if not action:
            distance_to_target = abs(character.position - action_target.position) if action_target else 999
            
            if (not used_spell_slot and character.spell_slots.get(1, 0) > 0 and 
                not resource_status['conserve_slots']):
                
                if distance_to_target > 10:
                    gb_action = self._get_guiding_bolt_action(character)
                    if gb_action and action_target:
                        action = gb_action
                        used_spell_slot = True
                        print(f"[TACTICAL AI] {character.name}: Target far away, using ranged spell!")

            if not action:
                attack_action = AttackAction(character.equipped_weapon)
                
                if resource_status['conserve_slots']:
                    character._conserving_slots_for_healing = True
                    print(f"[AI CONTROL] {character.name}: Attack without Divine Smite (conserving slots)")
                else:
                    character._conserving_slots_for_healing = False
                    
                action = attack_action

        # --- SEARING SMITE SETUP (PHB 2024) ---
        # In 2024, Searing Smite is cast AFTER hitting, not before
        # So we just set a flag to indicate we want to use it on the next successful melee hit
        if (not used_spell_slot and character.spell_slots.get(1, 0) > 0 and
                not resource_status['conserve_slots']):
            
            target_has_searing_smite = False
            if action_target and hasattr(action_target, 'searing_smite_effect'):
                target_has_searing_smite = action_target.searing_smite_effect.get('active', False)
            
            # Set up Searing Smite for the next melee attack
            if not target_has_searing_smite and isinstance(action, AttackAction):
                # Check if it's a melee weapon
                weapon = action.weapon
                is_melee = not (hasattr(weapon, 'properties') and 'Ranged' in weapon.properties)
                
                if is_melee:
                    from spells.level_1.searing_smite import searing_smite
                    if searing_smite in getattr(character, 'prepared_spells', []):
                        character._pending_searing_smite = True
                        print(f"[AI CONTROL] {character.name}: Will use Searing Smite if next melee attack hits")
                    else:
                        print(f"[AI CONTROL] {character.name}: Searing Smite not prepared")
                else:
                    print(f"[AI CONTROL] {character.name}: Ranged weapon, cannot use Searing Smite")
            elif target_has_searing_smite:
                print(f"[AI CONTROL] {character.name}: Target already has Searing Smite, skipping")
            elif not isinstance(action, AttackAction):
                print(f"[AI CONTROL] {character.name}: Not attacking, no Searing Smite setup")

        # SAFETY CHECK: Ensure we always have a valid action
        if not action:
            action = AttackAction(character.equipped_weapon)
            print(f"[FALLBACK] {character.name}: No action set, defaulting to attack")
        
        if not action_target:
            action_target = character  # Default to self if no target
            print(f"[FALLBACK] {character.name}: No target set, defaulting to self")

        # MISSING RETURN STATEMENT - THIS WAS THE BUG!
        return {
            'action': action,
            'bonus_action': bonus_action,
            'action_target': action_target,
            'bonus_action_target': bonus_action_target
        }

    def _assess_critical_survival(self, character, target):
        """NEW: Assess if character is in a life-threatening situation requiring emergency response."""
        our_hp_percent = character.hp / character.max_hp
        is_grappled = hasattr(character, 'is_grappled') and character.is_grappled
        
        # Calculate predicted damage if grappled (crush damage estimate)
        predicted_crush_damage = 0
        if is_grappled and hasattr(character, 'grappler'):
            # Estimate crush damage based on grappler's strength
            grappler = character.grappler
            if hasattr(grappler, 'stats'):
                # Typical crush damage is 2d8 + STR mod for large constrictors
                from core import get_ability_modifier
                str_mod = get_ability_modifier(grappler.stats.get('str', 10))
                predicted_crush_damage = 9 + str_mod  # 2d8 average (9) + STR mod
        
        # Critical survival thresholds
        critical_hp_threshold = 0.25  # 25%
        emergency_hp_threshold = 0.15  # 15%
        
        # Check if we'll likely die next turn
        will_likely_die = (character.hp <= predicted_crush_damage and predicted_crush_damage > 0)
        
        # Emergency healing needed if:
        # 1. HP < 15% regardless of situation
        # 2. HP < 25% and grappled (due to automatic crush damage)
        # 3. Predicted to die next turn from crush damage
        needs_emergency_healing = (
            our_hp_percent <= emergency_hp_threshold or
            (our_hp_percent <= critical_hp_threshold and is_grappled) or
            will_likely_die
        )
        
        # Override conservation if in critical survival mode
        override_conservation = needs_emergency_healing
        
        if needs_emergency_healing:
            reason = []
            if our_hp_percent <= emergency_hp_threshold:
                reason.append(f"HP critically low ({our_hp_percent:.1%})")
            if is_grappled and predicted_crush_damage > 0:
                reason.append(f"grappled facing {predicted_crush_damage} crush damage")
            if will_likely_die:
                reason.append("predicted death next turn")
            
            print(f"[CRITICAL SURVIVAL] {character.name}: EMERGENCY - {', '.join(reason)}")
        
        return {
            'needs_emergency_healing': needs_emergency_healing,
            'override_conservation': override_conservation,
            'predicted_crush_damage': predicted_crush_damage,
            'will_likely_die': will_likely_die,
            'our_hp_percent': our_hp_percent
        }

    def _assess_spell_slot_conservation(self, character, survival_override=False):
        """Assess whether to conserve spell slots for emergency healing."""
        total_slots = sum(character.spell_slots.values())
        our_hp_percent = character.hp / character.max_hp
        
        from spells.level_1.cure_wounds import cure_wounds
        has_cure_wounds_prepared = cure_wounds in getattr(character, 'prepared_spells', [])
        
        # MODIFIED: Don't conserve if survival override is active
        if survival_override:
            print(f"[RESOURCE AI] {character.name}: SURVIVAL OVERRIDE - Not conserving slots for emergency healing")
            return {
                'conserve_slots': False,
                'reason': "SURVIVAL OVERRIDE - Emergency healing needed",
                'total_slots': total_slots,
                'has_cure_wounds_prepared': has_cure_wounds_prepared
            }
        
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

    def _assess_grapple_situation(self, character, target, survival_status):
        """ENHANCED: Assess whether to escape grapple with survival context."""
        if not hasattr(character, 'is_grappled') or not character.is_grappled:
            return {'should_escape': False, 'reason': 'Not grappled'}
        
        our_hp_percent = character.hp / character.max_hp
        
        # Calculate escape chance
        from core import get_ability_modifier
        athletics_mod = get_ability_modifier(character.stats['str'])
        if 'Athletics' in getattr(character, 'skill_proficiencies', []):
            athletics_mod += character.get_proficiency_bonus()
        
        escape_dc = getattr(character, 'grapple_escape_dc', 14)
        escape_chance = ((21 + athletics_mod - escape_dc) / 20.0) * 100
        
        # FIXED: ALWAYS try to escape when grappled unless truly hopeless
        should_escape = True
        reason = f"Grappled - must escape to regain mobility (escape chance: {escape_chance:.0f}%)"
        
        # Only exception: critically low HP (≤10%) AND terrible escape chance (≤15%)
        if our_hp_percent <= 0.10 and escape_chance <= 15:
            should_escape = False
            reason = f"Critically low HP ({our_hp_percent:.1%}) with hopeless escape chance ({escape_chance:.0f}%) - attacking instead"
        
        return {
            'should_escape': should_escape,
            'reason': reason,
            'escape_chance': escape_chance
        }

    def _assess_healing_priority(self, character, combatants, resource_status, survival_status):
        """ENHANCED: Assess healing needs with survival context."""
        allies = [c for c in combatants if c.is_alive and c != character and hasattr(c, 'spell_slots')]
        heal_target = character

        all_possible_targets = [character] + allies
        most_injured = min(all_possible_targets, key=lambda c: c.hp / c.max_hp)

        heal_target = most_injured
        hp_percent = heal_target.hp / heal_target.max_hp

        # ENHANCED: Use survival status for thresholds
        if survival_status['needs_emergency_healing']:
            critical_healing = True
            moderate_healing = False
            print(f"[HEALING DEBUG] EMERGENCY mode - forcing critical healing")
        elif hasattr(character, 'is_grappled') and character.is_grappled:
            # More aggressive when grappled
            critical_healing = hp_percent <= 0.40  # 40% when grappled (was 50%)
            moderate_healing = hp_percent <= 0.70  # 70% when grappled
        else:
            # Normal thresholds when not grappled
            critical_healing = hp_percent <= 0.35  # 35% or less HP
            moderate_healing = hp_percent <= 0.65  # 65% or less HP

        from spells.level_1.cure_wounds import cure_wounds
        cure_wounds_prepared = cure_wounds in getattr(character, 'prepared_spells', [])
        has_cure_wounds_slots = character.spell_slots.get(1, 0) > 0
        
        # MODIFIED: In survival mode, always allow Cure Wounds regardless of conservation
        has_cure_wounds = cure_wounds_prepared and has_cure_wounds_slots
        has_lay_on_hands = character.lay_on_hands_pool > 0

        print(f"[HEALING DEBUG] HP: {character.hp}/{character.max_hp} ({hp_percent:.1%})")
        print(f"[HEALING DEBUG] Cure Wounds available: {has_cure_wounds} (prep: {cure_wounds_prepared}, slots: {has_cure_wounds_slots})")
        print(f"[HEALING DEBUG] Lay on Hands pool: {character.lay_on_hands_pool}")

        use_cure_wounds = False
        use_lay_on_hands = False

        if critical_healing:
            if has_cure_wounds and (not resource_status['conserve_slots'] or survival_status['needs_emergency_healing']):
                # Prefer Cure Wounds for critical healing
                use_cure_wounds = True
                if survival_status['needs_emergency_healing']:
                    print(f"[HEALING AI] EMERGENCY healing: Cure Wounds (~11.0 HP) - conservation overridden")
                else:
                    cure_avg = 9.0 + character.get_spellcasting_modifier()
                    loh_heal = min(character.lay_on_hands_pool, 15)
                    print(f"[HEALING AI] Critical healing: Cure Wounds (~{cure_avg:.1f} HP) vs Lay on Hands ({loh_heal} HP) - choosing Cure Wounds")
            elif has_lay_on_hands:
                use_lay_on_hands = True
                print(f"[HEALING AI] Critical healing: No Cure Wounds available, using Lay on Hands")

        elif moderate_healing:
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
        
        should_retreat = False
        reason = ""
        
        from spells.level_1.guiding_bolt import guiding_bolt
        has_guiding_bolt = (character.spell_slots.get(1, 0) > 0 and
                           guiding_bolt in getattr(character, 'prepared_spells', []))
        
        if our_hp_percent <= 0.40 and has_guiding_bolt:
            if current_distance <= 10:
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
    
    def _assess_channel_divinity_usage(self, character, grapple_decision):
        """Assess whether to use Channel Divinity options."""
        if not hasattr(character, 'channel_divinity_uses') or character.channel_divinity_uses <= 0:
            return {'should_use': False, 'option': None, 'reason': 'No Channel Divinity uses remaining'}
        
        # Peerless Athlete for grapple escape
        if grapple_decision['should_escape']:
            # FIXED: Check if Peerless Athlete is already active
            if getattr(character, 'peerless_athlete_active', False):
                return {'should_use': False, 'option': None, 'reason': 'Peerless Athlete already active (1 hour duration)'}
            
            # Check if we have Peerless Athlete available
            if hasattr(character, 'channel_divinity_options'):
                for option in character.channel_divinity_options:
                    if option.name == "Peerless Athlete":
                        return {
                            'should_use': True,
                            'option': 'Peerless Athlete',
                            'reason': f"Use Peerless Athlete for advantage on escape attempt (improves {grapple_decision['escape_chance']:.0f}% chance)"
                        }
        
        return {'should_use': False, 'option': None, 'reason': 'No beneficial Channel Divinity option for current situation'}
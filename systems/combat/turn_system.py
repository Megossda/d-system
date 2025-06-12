# File: systems/combat/turn_system.py
"""Global turn management system."""

def execute_creature_turn(creature, combatants):
    """Execute a creature's turn using global turn system."""
    # Reset turn state
    creature.has_used_action = False
    creature.has_used_bonus_action = False
    creature.has_used_reaction = False
    
    # Process start of turn effects
    creature.process_effects_on_turn_start()
    if not creature.is_alive:
        return
    
    # Get AI decision
    chosen_actions = creature.ai_brain.choose_actions(creature, combatants)
    
    # Execute movement
    execute_movement_phase(creature, chosen_actions, combatants)
    
    # Execute bonus action
    execute_bonus_action_phase(creature, chosen_actions)
    
    # Execute action
    execute_action_phase(creature, chosen_actions)
    
    # Log unused reaction
    print("REACTION: (Available)" if not creature.has_used_reaction else "REACTION: (Used)")

def execute_movement_phase(creature, chosen_actions, combatants):
    """Execute movement phase using global movement system."""
    # Implementation would use global movement and positioning systems
    print("MOVEMENT: (Global turn system)")

def execute_bonus_action_phase(creature, chosen_actions):
    """Execute bonus action phase."""
    bonus_action = chosen_actions.get('bonus_action')
    if bonus_action and not creature.has_used_bonus_action:
        bonus_target = chosen_actions.get('bonus_action_target')
        bonus_action.execute(creature, bonus_target, "BONUS ACTION")
        creature.has_used_bonus_action = True
    else:
        print("BONUS ACTION: (None)")

def execute_action_phase(creature, chosen_actions):
    """Execute action phase."""
    action = chosen_actions.get('action')
    if action and not creature.has_used_action:
        action_target = chosen_actions.get('action_target')
        
        # Handle special octopus tentacle action
        if isinstance(action, str) and action == 'tentacle_attack':
            if hasattr(creature, 'tentacle_attack'):
                success = creature.tentacle_attack(action_target, "ACTION")
                if success:
                    creature.has_used_action = True
        else:
            action.execute(creature, action_target, "ACTION")
            creature.has_used_action = True
    else:
        print("ACTION: (None)")
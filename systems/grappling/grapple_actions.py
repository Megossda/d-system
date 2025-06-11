# File: systems/grappling/grapple_actions.py
"""
Universal grapple actions that any creature can use.
These mirror our working action system but in reusable form.
"""

from actions.base_actions import Action
from .universal_grapple import UniversalGrappling


class UniversalGrappleActions:
    """Factory for creating standardized grapple actions."""

    @staticmethod
    def create_grapple_attack_action(damage_dice, save_dc=None, attack_name="Grapple", 
                                   damage_type="Bludgeoning", range_ft=5, method="attack"):
        """
        Create a grapple attack action (like PC unarmed strike grapple).
        
        Args:
            damage_dice: Damage dice (e.g., "1d4" for unarmed strike)
            save_dc: If None, calculates based on creature stats
            attack_name: Name of the attack
            damage_type: Type of damage
            range_ft: Range in feet
            method: "attack" for attack roll, "save" for saving throw
        """
        return GrappleAttackAction(damage_dice, save_dc, attack_name, damage_type, range_ft, method)

    @staticmethod
    def create_grapple_save_action(damage_dice, save_dc, attack_name="Constrict", 
                                 damage_type="Bludgeoning", range_ft=10):
        """
        Create a grapple save action (like Giant Constrictor Snake).
        
        Args:
            damage_dice: Damage dice (e.g., "2d8")
            save_dc: DC for the saving throw
            attack_name: Name of the attack
            damage_type: Type of damage
            range_ft: Range in feet
        """
        return GrappleAttackAction(damage_dice, save_dc, attack_name, damage_type, range_ft, "save")

    @staticmethod
    def create_escape_action():
        """Create a universal escape grapple action."""
        return UniversalEscapeGrappleAction()

    @staticmethod
    def create_crush_action(damage_dice="2d8", damage_type="Bludgeoning", action_name="Crush"):
        """
        Create a crush action for creatures that grapple.
        
        Args:
            damage_dice: Damage dice for the crush
            damage_type: Type of damage
            action_name: Name of the action
        """
        return UniversalCrushAction(damage_dice, damage_type, action_name)


class GrappleAttackAction(Action):
    """Universal grapple attack action that any creature can use."""

    def __init__(self, damage_dice, save_dc, attack_name, damage_type, range_ft, method):
        super().__init__(f"{attack_name} (Grapple)")
        self.damage_dice = damage_dice
        self.save_dc = save_dc
        self.attack_name = attack_name
        self.damage_type = damage_type
        self.range_ft = range_ft
        self.method = method

    def execute(self, performer, target, action_type="ACTION"):
        """Execute the grapple attack using the universal system."""
        if not target:
            print(f"{action_type}: {performer.name} has no target to {self.attack_name.lower()}!")
            return False

        # Calculate save DC if not provided
        save_dc = self.save_dc
        if save_dc is None:
            from core import get_ability_modifier
            save_dc = 8 + get_ability_modifier(performer.stats['str']) + performer.get_proficiency_bonus()

        # Use the universal grappling system
        return UniversalGrappling.attempt_grapple(
            attacker=performer,
            target=target,
            save_dc=save_dc,
            damage_dice=self.damage_dice,
            damage_type=self.damage_type,
            attack_name=self.attack_name,
            range_ft=self.range_ft,
            method=self.method
        )


class UniversalEscapeGrappleAction(Action):
    """Universal escape grapple action - mirrors our working EscapeGrappleAction."""

    def __init__(self):
        super().__init__("Escape Grapple")

    def execute(self, performer, target=None, action_type="ACTION"):
        """Execute escape attempt using universal system."""
        return UniversalGrappling.attempt_escape(performer, action_type)


class UniversalCrushAction(Action):
    """Universal crush action for grappling creatures."""

    def __init__(self, damage_dice, damage_type, action_name):
        super().__init__(action_name)
        self.damage_dice = damage_dice
        self.damage_type = damage_type
        self.action_name = action_name

    def execute(self, performer, target=None, action_type="ACTION"):
        """Execute crush using universal system."""
        return UniversalGrappling.crush_grappled_target(
            crusher=performer,
            action_type=action_type,
            damage_dice=self.damage_dice,
            damage_type=self.damage_type
        )


# Convenience functions for quick action creation
def create_unarmed_grapple_action():
    """Create a standard PC unarmed strike grapple action."""
    return UniversalGrappleActions.create_grapple_attack_action(
        damage_dice="1d4",  # Standard unarmed strike
        attack_name="Unarmed Strike (Grapple)",
        method="attack"
    )

def create_constrictor_grapple_action():
    """Create a Giant Constrictor Snake style grapple action."""
    return UniversalGrappleActions.create_grapple_save_action(
        damage_dice="2d8",
        save_dc=14,
        attack_name="Constrict",
        range_ft=10
    )

def create_tentacle_grapple_action():
    """Create a tentacle grapple action (for future Giant Octopus)."""
    return UniversalGrappleActions.create_grapple_save_action(
        damage_dice="2d6",
        save_dc=16,
        attack_name="Tentacle",
        range_ft=15
    )
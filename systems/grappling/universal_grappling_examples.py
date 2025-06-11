# File: examples/universal_grappling_examples.py
"""
Examples showing how to use the Universal Grappling System.
These examples show how future creatures can use the system.
"""

from systems.grappling import UniversalGrappling, UniversalGrappleActions
from enemies.base_enemy import Enemy
from equipment.weapons.base_weapon import Weapon


# Example 1: Giant Octopus using the universal system
class GiantOctopus(Enemy):
    """Example of a new creature using the universal grappling system."""

    def __init__(self, name="Giant Octopus", position=0):
        tentacle = Weapon(
            name="Tentacle",
            damage_dice="2d6",
            damage_type="Bludgeoning",
            properties=['Reach', 'Grapple'],
            reach=15
        )

        super().__init__(
            name=name,
            level=1,
            hp=52,  # 8d12 + 8
            stats={'str': 17, 'dex': 13, 'con': 13, 'int': 4, 'wis': 10, 'cha': 4},
            weapon=tentacle,
            cr='1',
            position=position,
            speed=10  # Swim speed 60ft, but we'll simplify
        )

        # Add universal grapple actions
        tentacle_grapple = UniversalGrappleActions.create_grapple_save_action(
            damage_dice="2d6",
            save_dc=15,  # 8 + 3 (STR) + 2 (Prof) + 2 (special)
            attack_name="Tentacle",
            range_ft=15
        )
        
        self.available_actions.append(tentacle_grapple)

    def tentacle_attack(self, target):
        """Example of using the universal system directly."""
        return UniversalGrappling.attempt_grapple(
            attacker=self,
            target=target,
            save_dc=15,
            damage_dice="2d6",
            attack_name="Tentacle",
            range_ft=15,
            method="save"
        )


# Example 2: PC Fighter using unarmed strike grapple
class Fighter(Character):
    """Example of a PC using the universal grappling system."""

    def __init__(self, name, level, hp, stats, weapon, position=0):
        super().__init__(name, level, hp, stats, weapon, position=position)
        
        # Add universal grapple actions
        unarmed_grapple = UniversalGrappleActions.create_grapple_attack_action(
            damage_dice="1d4",  # Base unarmed strike damage
            attack_name="Unarmed Strike (Grapple)",
            method="attack"  # PC uses attack roll, not save
        )
        
        escape_action = UniversalGrappleActions.create_escape_action()
        
        self.available_actions.extend([unarmed_grapple, escape_action])

    def attempt_grapple(self, target):
        """Example of PC grappling using universal system."""
        from core import get_ability_modifier
        
        # PC grapple DC = 8 + STR mod + Prof bonus
        grapple_dc = 8 + get_ability_modifier(self.stats['str']) + self.get_proficiency_bonus()
        
        return UniversalGrappling.attempt_grapple(
            attacker=self,
            target=target,
            save_dc=grapple_dc,
            damage_dice="1d4",
            attack_name="Unarmed Strike",
            range_ft=5,
            method="attack"
        )


# Example 3: Roper using the universal system
class Roper(Enemy):
    """Example of another grappling creature using the universal system."""

    def __init__(self, name="Roper", position=0):
        tendril = Weapon(
            name="Tendril",
            damage_dice="1d6",
            damage_type="Piercing",
            properties=['Reach', 'Grapple'],
            reach=50  # Roper has very long reach!
        )

        super().__init__(
            name=name,
            level=1,
            hp=93,  # 11d12 + 22
            stats={'str': 18, 'dex': 8, 'con': 15, 'int': 7, 'wis': 16, 'cha': 6},
            weapon=tendril,
            cr='5',
            position=position,
            speed=10
        )

        # Roper can grapple up to 4 creatures at once with different tendrils
        self.grappled_targets = {}  # Track multiple grapples
        self.max_grapples = 4

        # Add universal grapple actions
        tendril_grapple = UniversalGrappleActions.create_grapple_save_action(
            damage_dice="1d6",
            save_dc=15,
            attack_name="Tendril",
            range_ft=50
        )
        
        # Roper can reel in grappled targets
        reel_action = UniversalGrappleActions.create_crush_action(
            damage_dice="1d6",
            damage_type="Piercing",
            action_name="Reel In"
        )
        
        self.available_actions.extend([tendril_grapple, reel_action])

    def can_grapple_more_targets(self):
        """Check if Roper can grapple additional targets."""
        current_grapples = len([t for t in self.grappled_targets.values() if t and t.is_alive])
        return current_grapples < self.max_grapples

    def tendril_grapple(self, target):
        """Roper's tendril attack using universal system."""
        if not self.can_grapple_more_targets():
            print(f"{self.name} cannot grapple more targets (max {self.max_grapples})")
            return False

        success = UniversalGrappling.attempt_grapple(
            attacker=self,
            target=target,
            save_dc=15,
            damage_dice="1d6",
            attack_name="Tendril",
            range_ft=50,
            method="save"
        )

        if success:
            # Track this grapple for multi-target management
            tendril_id = len(self.grappled_targets)
            self.grappled_targets[tendril_id] = target
            print(f"** {self.name} is now grappling {target.name} with tendril #{tendril_id} **")

        return success


# Example 4: How existing creatures could migrate (OPTIONAL - doesn't break current system)
class GiantConstrictorSnakeUniversal(Enemy):
    """
    OPTIONAL: Example of how Giant Constrictor Snake could use universal system.
    This is just an example - our current working snake stays unchanged!
    """

    def __init__(self, name="Giant Constrictor Snake (Universal)", position=0):
        snake_bite = Weapon(
            name="Bite",
            damage_dice="2d6",
            damage_type="Piercing",
            properties=['Reach'],
            reach=10
        )

        super().__init__(
            name=name,
            level=1,
            hp=60,
            stats={'str': 19, 'dex': 14, 'con': 12, 'int': 1, 'wis': 10, 'cha': 3},
            weapon=snake_bite,
            cr='2',
            position=position,
            speed=30
        )

        # Using universal actions instead of custom methods
        constrict_action = UniversalGrappleActions.create_grapple_save_action(
            damage_dice="2d8",
            save_dc=14,
            attack_name="Constrict",
            range_ft=10
        )
        
        crush_action = UniversalGrappleActions.create_crush_action(
            damage_dice="2d8",
            damage_type="Bludgeoning",
            action_name="Crush"
        )
        
        self.available_actions.extend([constrict_action, crush_action])

    def multiattack_universal(self, target):
        """Example multiattack using universal system."""
        print(f"ACTION: {self.name} uses Multiattack!")
        print(f"** Making a Bite attack and a Constrict attack **")

        # Bite attack (unchanged)
        self.bite_attack(target)

        # Constrict using universal system
        if target.is_alive:
            if not self.is_grappling:
                UniversalGrappling.attempt_grapple(
                    attacker=self,
                    target=target,
                    save_dc=14,
                    damage_dice="2d8",
                    attack_name="Constrict",
                    range_ft=10,
                    method="save"
                )
            else:
                print(f"--- Already grappling, cannot constrict another target ---")


# Example 5: Usage in combat scenarios
def demonstrate_universal_grappling():
    """Example of how the universal system would be used in combat."""
    
    # Create creatures
    octopus = GiantOctopus("Kraken Jr.", position=0)
    fighter = Fighter("Grog", level=5, hp=58, 
                     stats={'str': 16, 'dex': 14, 'con': 15, 'int': 10, 'wis': 12, 'cha': 8},
                     weapon=None, position=10)

    print("=== Universal Grappling System Demo ===")
    
    # Octopus attempts to grapple fighter
    print("\n--- Octopus Turn ---")
    octopus.tentacle_attack(fighter)
    
    # Fighter attempts to escape
    print("\n--- Fighter Turn ---")
    if fighter.is_grappled:
        UniversalGrappling.attempt_escape(fighter, "ACTION")
    
    # If still grappled, octopus crushes
    print("\n--- Octopus Turn 2 ---")
    if octopus.is_grappling:
        UniversalGrappling.crush_grappled_target(octopus, "ACTION", "2d6")


# Example 6: Condition validation
def validate_all_grapples(combatants):
    """Example of how to validate grapple states during combat."""
    from systems.grappling import GrappleConditionManager
    
    for combatant in combatants:
        GrappleConditionManager.validate_grapple_state(combatant)


if __name__ == "__main__":
    # This would only run if someone executes this example file
    demonstrate_universal_grappling()
# File: enemies/cr_half_1/giant_octopus.py
from ..base_enemy import Enemy
from equipment.weapons.base_weapon import Weapon
from systems.grappling import UniversalGrappling, UniversalGrappleActions
from core import roll_d20, get_ability_modifier, roll
from actions.special_actions import MultiattackAction


class GiantOctopus(Enemy):
    """A Giant Octopus - CR 1 challenge using Universal Grappling System - PHB 2024."""

    def __init__(self, name="Giant Octopus", position=0):
        # Natural weapons for the octopus
        tentacles = Weapon(
            name="Tentacles",
            damage_dice="2d6",
            damage_type="Bludgeoning",
            properties=['Reach', 'Grapple'],  # 10ft reach, grappling weapon
            reach=10
        )

        super().__init__(
            name=name,
            level=1,  # Minimal level for compatibility
            hp=45,  # 7d10 + 7
            stats={'str': 17, 'dex': 13, 'con': 13, 'int': 5, 'wis': 10, 'cha': 4},
            weapon=tentacles,
            armor=None,  # Natural AC
            shield=None,
            cr='1',  # CR 1 for Giant Octopus
            position=position,
            initiative_bonus=0,
            speed=10  # 10 ft. land, 60 ft. swim (simplified for our system)
        )

        from ai.enemy_ai.beast.giant_octopus_ai import GiantOctopusAI
        self.ai_brain = GiantOctopusAI()
        
        # Octopus-specific traits
        self.size = 'Large'
        self.can_breathe_underwater = True
        self.ink_cloud_used = False  # Track 1/day ink cloud usage
        
        # Octopus can grapple multiple targets with its 8 tentacles
        self.grappled_targets = []  # Track multiple grapples
        self.max_tentacles = 8
        
        # Add universal grapple action using our new system
        tentacle_grapple = UniversalGrappleActions.create_grapple_attack_action(
            damage_dice="2d6",
            save_dc=None,  # Will be calculated: 8 + STR(+3) + Prof(+2) = 13
            attack_name="Tentacles",
            damage_type="Bludgeoning",
            range_ft=10,
            method="attack"  # PHB 2024: Uses attack roll, not save
        )
        
        self.available_actions.append(tentacle_grapple)

    def calculate_ac(self):
        """Override AC calculation for natural armor"""
        return 11  # Natural armor from stat block
    
    def get_proficiency_bonus(self):
        """Override to use correct CR 1 proficiency bonus."""
        return 2  # CR 1 creatures have +2 proficiency bonus

    def tentacle_attack(self, target, action_type="ACTION"):
        """
        Octopus tentacle attack using Universal Grappling System.
        PHB 2024: Attack roll, 10ft reach, grapples Medium or smaller creatures.
        """
        if not self.is_alive or not target or not target.is_alive:
            return False

        # Check if we can grapple more targets
        active_grapples = len([t for t in self.grappled_targets if t and t.is_alive])
        if active_grapples >= self.max_tentacles:
            print(f"{action_type}: {self.name} has all tentacles occupied (max {self.max_tentacles})!")
            return False

        # Check target size (PHB 2024: Medium or smaller)
        target_size = getattr(target, 'size', 'Medium')
        if target_size not in ['Tiny', 'Small', 'Medium']:
            print(f"{action_type}: {self.name}'s tentacles cannot grapple {target_size} creatures!")
            return False

        # Check range (10ft reach)
        distance = abs(self.position - target.position)
        if distance > 10:
            print(f"TENTACLES: {self.name} tries to attack {target.name}, but is out of range (distance: {distance}ft, reach: 10ft)")
            return False

        print(f"TENTACLES: {self.name} attacks {target.name} (AC: {target.ac}) with Tentacles!")

        # Make attack roll (PHB 2024: Melee Attack Roll +5)
        attack_roll, _ = roll_d20()
        attack_modifier = get_ability_modifier(self.stats['str'])  # +3
        prof_bonus = self.get_proficiency_bonus()  # +2
        total_attack = attack_roll + attack_modifier + prof_bonus  # Should be +5

        print(f"ATTACK ROLL: {attack_roll} (1d20) +{attack_modifier} (STR) +{prof_bonus} (Prof) = {total_attack}")

        if total_attack >= target.ac or attack_roll == 20:
            is_crit = (attack_roll == 20)
            if is_crit:
                print(">>> CRITICAL HIT! <<<")
            else:
                print("The tentacle attack hits!")

            # Deal damage first
            damage = roll(self.equipped_weapon.damage_dice)
            if is_crit:
                crit_damage = roll(self.equipped_weapon.damage_dice)
                damage += crit_damage
                print(f"CRIT DAMAGE: Doubled dice from {self.equipped_weapon.damage_dice}")

            total_damage = damage + attack_modifier
            print(f"{self.name} deals {total_damage} bludgeoning damage ({damage} [{self.equipped_weapon.damage_dice}{'+ crit' if is_crit else ''}] +{attack_modifier} [STR])")
            target.take_damage(total_damage, attacker=self)

            # Apply grapple if target survives
            if target.is_alive:
                return self._apply_octopus_grapple(target)
        else:
            print("The tentacle attack misses.")
            return False

    def _apply_octopus_grapple(self, target):
        """Apply octopus-specific grapple using universal system."""
        # Calculate escape DC: 8 + STR mod + Prof = 8 + 3 + 2 = 13
        escape_dc = 8 + get_ability_modifier(self.stats['str']) + self.get_proficiency_bonus()
        
        # Apply standard grapple using universal system
        success = UniversalGrappling._apply_grapple_condition(self, target, escape_dc)
        
        if success:
            # Track this grapple for multi-target management
            self.grappled_targets.append(target)
            
            # PHB 2024: Octopus grapple also applies Restrained condition
            self._apply_restrained_condition(target)
            
            print(f"** {self.name} is grappling {target.name} with {len(self.grappled_targets)} of {self.max_tentacles} tentacles **")
        
        return success

    def _apply_restrained_condition(self, target):
        """Apply Restrained condition (PHB 2024: Grappled targets are also Restrained)."""
        target.is_restrained = True
        print(f"** {target.name} also has the Restrained condition! **")
        print(f"** Restrained: Speed 0, Advantage on attacks against it, Disadvantage on DEX saves **")

    def _remove_restrained_condition(self, target):
        """Remove Restrained condition when grapple ends."""
        if hasattr(target, 'is_restrained'):
            target.is_restrained = False
            print(f"** {target.name} is no longer restrained **")

    def squeeze_grappled_targets(self, action_type="ACTION"):
        """
        Squeeze all grappled targets (alternative to new tentacle attacks).
        This represents the octopus tightening its grip on all grappled creatures.
        """
        if not self.grappled_targets:
            print(f"{action_type}: {self.name} has no grappled targets to squeeze!")
            return False

        # Filter out dead/invalid targets
        valid_targets = [t for t in self.grappled_targets if t and t.is_alive and hasattr(t, 'is_grappled') and t.is_grappled]
        
        if not valid_targets:
            print(f"{action_type}: {self.name} has no valid targets to squeeze!")
            self.grappled_targets = []  # Clear invalid targets
            return False

        print(f"{action_type}: {self.name} squeezes all grappled creatures with its tentacles!")
        
        for target in valid_targets:
            # Deal damage to each grappled target
            damage = roll("2d6")
            total_damage = damage + get_ability_modifier(self.stats['str'])
            
            print(f"** {target.name} takes {total_damage} bludgeoning damage ({damage} [2d6] +{get_ability_modifier(self.stats['str'])} [STR]) **")
            target.take_damage(total_damage, attacker=self)

        print(f"** All grappled targets remain grappled and restrained! **")
        return True

    def release_grapple(self, target):
        """Release a specific grappled target (octopus choice)."""
        if target in self.grappled_targets:
            self.grappled_targets.remove(target)
            
            # Use universal system to clean up grapple
            UniversalGrappling._free_from_grapple(target, self)
            self._remove_restrained_condition(target)
            
            print(f"** {self.name} releases {target.name} from its tentacles **")

    def ink_cloud_reaction(self, action_type="REACTION"):
        """
        Ink Cloud reaction (1/Day) - PHB 2024.
        Trigger: Takes damage while underwater.
        """
        if self.ink_cloud_used:
            print(f"** {self.name} has already used its Ink Cloud today! **")
            return False

        # For simplicity, assume we're always "underwater" in our combat system
        print(f"{action_type}: {self.name} releases a cloud of ink!")
        print(f"** Ink fills a 10-foot cube centered on {self.name} **")
        print(f"** Area is Heavily Obscured for 1 minute **")
        print(f"** {self.name} moves up to its swim speed (simplified as movement) **")
        
        # Mark ink cloud as used
        self.ink_cloud_used = True
        
        # In a full implementation, this would create an area effect
        # For now, just log the effect
        return True

    def process_effects_on_turn_start(self):
        """Process ongoing effects and clean up invalid grapples."""
        super().process_effects_on_turn_start()

        # Clean up invalid grapples
        valid_targets = []
        for target in self.grappled_targets:
            if target and target.is_alive and hasattr(target, 'is_grappled') and target.is_grappled:
                valid_targets.append(target)
            else:
                print(f"** {self.name} releases invalid grapple target **")
                if target:
                    self._remove_restrained_condition(target)

        self.grappled_targets = valid_targets

    def take_damage(self, damage, attacker=None):
        """Override to handle grapple breaking on death and ink cloud reaction."""
        super().take_damage(damage, attacker)

        # Trigger ink cloud reaction if taking damage and still alive
        if self.is_alive and not self.ink_cloud_used and attacker:
            print(f"** {self.name} triggers Ink Cloud reaction! **")
            self.ink_cloud_reaction("REACTION")

        # If the octopus dies, release all grappled targets
        if not self.is_alive and self.grappled_targets:
            print(f"** {self.name} dies and releases all grappled creatures! **")
            for target in self.grappled_targets[:]:  # Copy list to avoid modification during iteration
                self.release_grapple(target)

    def take_turn(self, combatants):
        """Override take_turn to handle octopus-specific actions."""
        self.has_used_action = False
        self.has_used_bonus_action = False
        
        # Store combatants reference
        self.current_combatants = combatants
        
        chosen_actions = self.ai_brain.choose_actions(self, combatants)

        defender = chosen_actions.get('action_target') or next((c for c in combatants if c.is_alive and c != self), None)

        moved = False
        movement_executed = 0

        # Simple movement logic for octopus
        if defender and chosen_actions.get('action'):
            action = chosen_actions.get('action')
            
            # Basic movement for attacks
            if isinstance(action, AttackAction) or isinstance(action, str):
                current_distance = abs(self.position - defender.position) if defender else 0
                
                # If too far for tentacle attack (10ft reach), move closer
                if current_distance > 10:
                    needed_movement = current_distance - 10
                    actual_movement = min(self.speed, needed_movement)
                    
                    if actual_movement > 0:
                        direction = 1 if defender.position > self.position else -1
                        self.position += actual_movement * direction
                        movement_executed = actual_movement
                        print(f"MOVEMENT: {self.name} moves {movement_executed} feet towards {defender.name}.")
                        moved = True

        if not moved:
            print("MOVEMENT: (None)")

        # Bonus action (octopus doesn't have bonus actions in PHB 2024)
        print("BONUS ACTION: (None)")

        # Handle special octopus actions
        action = chosen_actions.get('action')
        if action and not self.has_used_action:
            action_target = chosen_actions.get('action_target')
            
            # Handle special octopus actions
            if isinstance(action, str):
                if action == 'tentacle_attack':
                    if action_target:
                        success = self.tentacle_attack(action_target, "ACTION")
                        if success:
                            self.has_used_action = True
                elif action == 'squeeze_grappled_targets':
                    success = self.squeeze_grappled_targets("ACTION")
                    if success:
                        self.has_used_action = True
            else:
                # Normal action execution
                action.execute(self, action_target, "ACTION")
                self.has_used_action = True
        else:
            print("ACTION: (None)")

        print("REACTION: (Not used)")

    def can_grapple_more_targets(self):
        """Check if octopus can grapple additional targets."""
        active_grapples = len([t for t in self.grappled_targets if t and t.is_alive])
        return active_grapples < self.max_tentacles

    def __str__(self):
        """Enhanced string representation with grapple info."""
        base_info = super().__str__()
        
        if self.grappled_targets:
            active_grapples = len([t for t in self.grappled_targets if t and t.is_alive])
            grapple_info = f"\nGrappling: {active_grapples}/{self.max_tentacles} tentacles in use"
            base_info += grapple_info
        
        if self.ink_cloud_used:
            base_info += "\nInk Cloud: Used (1/Day)"
        
        return base_info
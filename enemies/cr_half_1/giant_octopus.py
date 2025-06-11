# File: enemies/cr_half_1/giant_octopus.py
from ..base_enemy import Enemy
from equipment.weapons.base_weapon import Weapon
from core import roll_d20, get_ability_modifier, roll
from actions.base_actions import AttackAction


class GiantOctopus(Enemy):
    """A Giant Octopus - CR 1 challenge using PHB 2024 rules."""

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
            hp=45,  # 7d10 + 7 (PHB 2024 stat block)
            stats={'str': 17, 'dex': 13, 'con': 13, 'int': 5, 'wis': 10, 'cha': 4},
            weapon=tentacles,
            armor=None,  # Natural AC
            shield=None,
            cr='1',  # CR 1 for Giant Octopus
            position=position,
            initiative_bonus=1,  # PHB 2024: DEX modifier (+1)
            speed=10  # 10 ft. land, 60 ft. swim (simplified for our system)
        )
        
        # PHB 2024: Add skill proficiencies after initialization
        self.skill_proficiencies = ['Perception', 'Stealth']

        # Import AI after class is defined to avoid circular imports
        try:
            from ai.enemy_ai.beast.giant_octopus_ai import GiantOctopusAI
            self.ai_brain = GiantOctopusAI()
        except ImportError:
            # Fallback to base AI if octopus AI not available
            from ai.base_ai import AIBrain
            self.ai_brain = AIBrain()
        
        # Octopus-specific traits (PHB 2024)
        self.size = 'Large'
        self.can_breathe_underwater = True
        self.water_breathing = True
        self.breath_holding_time = 60  # 1 hour outside water (in minutes)
        self.darkvision = 60  # 60 ft. darkvision
        self.passive_perception = 14  # 10 + Perception skill (+4)
        self.ink_cloud_used = False  # Track 1/day ink cloud usage
        
        # Custom skill bonuses to match PHB 2024 stat block
        self.custom_skill_bonuses = {
            'Perception': 4,   # PHB 2024: +4 (suggests expertise or special bonus)
            'Stealth': 5       # PHB 2024: +5 (suggests expertise or special bonus)
        }
        
        # PHB 2024: Octopus grapples ONE creature with ALL tentacles
        self.grappled_target = None  # Single target, not multiple
        self.is_grappling = False

    def calculate_ac(self):
        """Override AC calculation for natural armor"""
        return 11  # Natural armor from stat block
    
    def get_proficiency_bonus(self):
        """Override to use correct CR 1 proficiency bonus."""
        return 2  # CR 1 creatures have +2 proficiency bonus

    def tentacle_attack(self, target, action_type="ACTION"):
        """
        Octopus tentacle attack - PHB 2024 rules.
        Uses attack roll, 10ft reach, grapples one creature with all tentacles.
        """
        if not self.is_alive or not target or not target.is_alive:
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

        # PHB 2024: Can only grapple one creature at a time with all tentacles
        if self.is_grappling and self.grappled_target and self.grappled_target != target:
            print(f"TENTACLES: {self.name} is already grappling {self.grappled_target.name} with all eight tentacles!")
            print(f"Cannot grapple {target.name} - must attack current target or release first")
            return False

        print(f"TENTACLES: {self.name} attacks {target.name} (AC: {target.ac}) with Tentacles!")

        # Make attack roll (PHB 2024: Melee Attack Roll +5)
        attack_roll, _ = roll_d20()
        
        # Check if target is restrained (gives advantage to attacks against it)
        has_advantage = hasattr(target, 'is_restrained') and target.is_restrained
        if has_advantage:
            # Reroll for advantage
            second_roll, _ = roll_d20()
            attack_roll = max(attack_roll, second_roll)
            print(f"** Attack has Advantage (target is Restrained) - using higher of two rolls **")
        
        attack_modifier = get_ability_modifier(self.stats['str'])  # +3
        prof_bonus = self.get_proficiency_bonus()  # +2
        total_attack = attack_roll + attack_modifier + prof_bonus  # Should be +5

        advantage_text = " (with Advantage)" if has_advantage else ""
        print(f"ATTACK ROLL: {attack_roll} (1d20{advantage_text}) +{attack_modifier} (STR) +{prof_bonus} (Prof) = {total_attack}")

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

            # Apply grapple if target survives AND octopus isn't already grappling this target
            if target.is_alive:
                return self._apply_octopus_grapple(target)
            return True
        else:
            print("The tentacle attack misses.")
            return False

    def _apply_octopus_grapple(self, target):
        """Apply octopus-specific grapple with PHB 2024 rules."""
        # PHB 2024: Escape DC 13 (fixed, not calculated)
        escape_dc = 13
        
        # Apply grapple condition
        self.is_grappling = True
        self.grappled_target = target
        target.is_grappled = True
        target.grappler = self
        target.grapple_escape_dc = escape_dc
        
        print(f"** {target.name} is GRAPPLED by {self.name}! **")
        print(f"** {target.name} has the Grappled condition: Speed 0, disadvantage on attacks vs others **")
        print(f"** Escape DC: {escape_dc} (STR Athletics or DEX Acrobatics check) **")
        
        # PHB 2024: Octopus grapple also applies Restrained condition
        target.is_restrained = True
        print(f"** {target.name} also has the Restrained condition! **")
        print(f"** Restrained: Speed 0, Advantage on attacks against it, Disadvantage on DEX saves **")
        
        print(f"** {self.name} has entangled {target.name} with ALL EIGHT tentacles **")
        
        return True

    def release_grapple(self, target=None):
        """Release the grappled target."""
        if self.is_grappling and self.grappled_target:
            target_to_release = target or self.grappled_target
            
            # Remove octopus-specific condition first (Restrained)
            if hasattr(target_to_release, 'is_restrained'):
                target_to_release.is_restrained = False
                print(f"** {target_to_release.name} is no longer restrained **")
            
            # Remove standard grapple conditions
            if hasattr(target_to_release, 'is_grappled'):
                target_to_release.is_grappled = False
            if hasattr(target_to_release, 'grappler'):
                delattr(target_to_release, 'grappler')
            if hasattr(target_to_release, 'grapple_escape_dc'):
                delattr(target_to_release, 'grapple_escape_dc')
            
            print(f"** {target_to_release.name} is no longer grappled **")
            
            # Update octopus state
            self.is_grappling = False
            self.grappled_target = None
            
            print(f"** {self.name} releases {target_to_release.name} from its tentacles **")

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
        return True

    def process_effects_on_turn_start(self):
        """Process ongoing effects and validate grapples."""
        super().process_effects_on_turn_start()

        # Process Searing Smite ongoing damage (if any)
        if hasattr(self, 'searing_smite_effect') and self.searing_smite_effect.get('active', False):
            effect = self.searing_smite_effect
            dice_count = effect['dice_count']
            save_dc = effect['save_dc']
            caster = effect['caster']
            
            # Deal ongoing fire damage
            ongoing_damage = 0
            for _ in range(dice_count):
                ongoing_damage += roll('1d6')
            
            print(f"** {self.name} takes {ongoing_damage} fire damage ({dice_count}d6) from Searing Smite! **")
            self.take_damage(ongoing_damage, attacker=caster)
            
            # Constitution saving throw to end the effect
            if self.is_alive:
                print(f"** {self.name} makes a Constitution saving throw to extinguish the flames **")
                if self.make_saving_throw('con', save_dc):
                    print(f"** {self.name} succeeds and extinguishes the searing flames! **")
                    self.searing_smite_effect['active'] = False
                    del self.searing_smite_effect
                else:
                    print(f"** {self.name} fails and continues burning! **")

        # Basic grapple validation
        if self.is_grappling and (not self.grappled_target or not self.grappled_target.is_alive):
            print(f"** {self.name} releases its grapple (target no longer valid) **")
            self.is_grappling = False
            self.grappled_target = None

    def take_damage(self, damage, attacker=None):
        """Override to handle grapple breaking on death and ink cloud reaction."""
        super().take_damage(damage, attacker)

        # Trigger ink cloud reaction if taking damage and still alive
        if self.is_alive and not self.ink_cloud_used and attacker:
            print(f"** {self.name} triggers Ink Cloud reaction! **")
            self.ink_cloud_reaction("REACTION")

        # If the octopus dies, release grappled target
        if not self.is_alive and self.is_grappling:
            print(f"** {self.name} dies and releases its grappled creature! **")
            self.release_grapple()

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
            if isinstance(action, str) and action == 'tentacle_attack':
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

        # Handle octopus actions - ONLY Tentacles action exists
        action = chosen_actions.get('action')
        if action and not self.has_used_action:
            action_target = chosen_actions.get('action_target')
            
            # Handle octopus Tentacles action
            if isinstance(action, str) and action == 'tentacle_attack':
                if action_target:
                    success = self.tentacle_attack(action_target, "ACTION")
                    if success:
                        self.has_used_action = True
            else:
                # Normal action execution (should only be AttackAction with tentacles)
                action.execute(self, action_target, "ACTION")
                self.has_used_action = True
        else:
            print("ACTION: (None)")

        print("REACTION: (Not used)")

    def __str__(self):
        """Enhanced string representation with grapple info."""
        base_info = super().__str__()
        
        if self.is_grappling and self.grappled_target:
            grapple_info = f"\nGrappling: {self.grappled_target.name} with all 8 tentacles"
            base_info += grapple_info
        
        if self.ink_cloud_used:
            base_info += "\nInk Cloud: Used (1/Day)"
        
        return base_info
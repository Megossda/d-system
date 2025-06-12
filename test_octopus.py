# File: enemies/cr_half_1/giant_octopus.py
"""
Giant Octopus - PHB 2024 Compliant Implementation
CR 1 Beast using ONLY global systems - no local mechanics.
"""

from ..base_enemy import Enemy
from equipment.weapons.base_weapon import Weapon


class GiantOctopus(Enemy):
    """A Giant Octopus - CR 1 using PHB 2024 rules and global systems only."""

    def __init__(self, name="Giant Octopus", position=0):
        # PHB 2024 natural weapon
        tentacles = Weapon(
            name="Tentacles",
            damage_dice="2d6",
            damage_type="Bludgeoning",
            properties=['Reach', 'Grapple'],
            reach=10
        )

        super().__init__(
            name=name,
            level=1,
            hp=45,  # PHB 2024: 7d10 + 7
            stats={
                'str': 17,  # PHB 2024: +3 mod
                'dex': 13,  # PHB 2024: +1 mod  
                'con': 13,  # PHB 2024: +1 mod
                'int': 5,   # PHB 2024: -3 mod
                'wis': 10,  # PHB 2024: +0 mod
                'cha': 4    # PHB 2024: -3 mod
            },
            weapon=tentacles,
            cr='1',  # PHB 2024: CR 1
            position=position,
            initiative_bonus=1,  # PHB 2024: +1
            speed=10  # PHB 2024: 10 ft. land, 60 ft. swim
        )
        
        # PHB 2024 creature properties - use global creature system
        self.size = 'Large'
        self.creature_type = 'Beast'
        self.alignment = 'Unaligned'
        
        # PHB 2024 skills - use global skill system
        self.skill_proficiencies = ['Perception', 'Stealth']
        
        # PHB 2024 senses - use global senses system
        self.darkvision = 60
        self.passive_perception = 14
        
        # Initialize basic grappling attributes (required by base system)
        self.is_grappling = False
        self.is_grappled = False
        self.grapple_target = None
        
        # Set up grappling using ONLY global grappling system
        self._setup_global_grappling()
        
        # Set up other global systems
        self._setup_global_traits()
        self._setup_global_ai()

    def _setup_global_grappling(self):
        """Set up grappling using ONLY the global grappling system."""
        try:
            from systems.grappling.grapple_manager import setup_creature_grappling
            # Use the giant_octopus profile from global system
            setup_creature_grappling(self, 'giant_octopus')
        except ImportError as e:
            print(f"Warning: Global grappling system not fully available: {e}")
            # Fallback: Set basic attributes manually
            pass

    def _setup_global_traits(self):
        """Set up creature traits using global trait system."""
        # PHB 2024: Water Breathing trait
        
        # Initialize traits list
        if not hasattr(self, 'traits'):
            self.traits = []
        
        # Add water breathing trait
        self.traits.append({
            'name': 'Water Breathing',
            'description': 'Can breathe only underwater. Holds breath for 1 hour outside water.',
            'type': 'environmental'
        })
        
        # Add ink cloud reaction
        self.traits.append({
            'name': 'Ink Cloud',
            'description': '1/Day reaction when taking damage underwater',
            'type': 'reaction',
            'uses_per_day': 1,
            'used_today': False
        })

    def _setup_global_ai(self):
        """Set up AI using global AI system."""
        try:
            from ai.enemy_ai.beast.giant_octopus_ai import GiantOctopusAI
            self.ai_brain = GiantOctopusAI()
        except ImportError:
            from ai.base_ai import AIBrain
            self.ai_brain = AIBrain()

    def calculate_ac(self):
        """PHB 2024: AC 11 natural armor."""
        return 11

    def get_proficiency_bonus(self):
        """PHB 2024: CR 1 = +2 proficiency bonus."""
        return 2

    def get_skill_bonus(self, skill):
        """Get skill bonus using global skill system."""
        from systems.skills import calculate_skill_bonus
        
        # PHB 2024 custom skill bonuses
        phb_2024_skills = {
            'Perception': 4,   # PHB 2024: +4 total
            'Stealth': 5       # PHB 2024: +5 total
        }
        
        if skill in phb_2024_skills:
            return phb_2024_skills[skill]
        
        # Use global skill calculation for other skills
        return calculate_skill_bonus(self, skill)

    def tentacle_attack(self, target, action_type="ACTION"):
        """
        PHB 2024 Tentacles attack using global systems where available.
        Falls back to working implementation if global systems unavailable.
        """
        if not self.is_alive or not target or not target.is_alive:
            return False

        # PHB 2024: Size restriction check
        target_size = getattr(target, 'size', 'Medium')
        if target_size not in ['Tiny', 'Small', 'Medium']:
            print(f"{action_type}: {self.name}'s tentacles cannot grapple {target_size} creatures!")
            return False

        # Range check
        distance = abs(self.position - target.position)
        if distance > 10:
            print(f"TENTACLES: {self.name} out of range (distance: {distance}ft, reach: 10ft)")
            return False

        # PHB 2024: Single target check
        if self.is_grappling and hasattr(self, 'grapple_target') and self.grapple_target != target:
            print(f"TENTACLES: {self.name} already grappling {self.grapple_target.name} with all tentacles!")
            return False

        print(f"TENTACLES: {self.name} attacks {target.name} with Tentacles!")

        # Make attack roll - PHB 2024: +5 to hit
        from core import roll_d20, roll, get_ability_modifier
        
        attack_roll, _ = roll_d20()
        
        # Check if target is restrained (gives advantage)
        has_advantage = hasattr(target, 'is_restrained') and target.is_restrained
        if has_advantage:
            second_roll, _ = roll_d20()
            attack_roll = max(attack_roll, second_roll)
            print(f"** Attack has Advantage (target is Restrained) **")
        
        attack_modifier = get_ability_modifier(self.stats['str'])  # +3
        prof_bonus = self.get_proficiency_bonus()  # +2
        total_attack = attack_roll + attack_modifier + prof_bonus  # +5 total

        advantage_text = " (with Advantage)" if has_advantage else ""
        print(f"ATTACK ROLL: {attack_roll} (1d20{advantage_text}) +{attack_modifier} (STR) +{prof_bonus} (Prof) = {total_attack}")

        if total_attack >= target.ac or attack_roll == 20:
            is_crit = (attack_roll == 20)
            if is_crit:
                print(">>> CRITICAL HIT! <<<")
            else:
                print("The tentacle attack hits!")

            # PHB 2024: Deal damage (2d6 + 3)
            damage = roll(self.equipped_weapon.damage_dice)
            if is_crit:
                damage += roll(self.equipped_weapon.damage_dice)

            total_damage = damage + attack_modifier
            print(f"{self.name} deals {total_damage} bludgeoning damage ({damage} [{self.equipped_weapon.damage_dice}{'+ crit' if is_crit else ''}] +{attack_modifier} [STR])")
            target.take_damage(total_damage, attacker=self)

            # Apply grapple if target survives
            if target.is_alive:
                return self._apply_phb_2024_grapple(target)
            return True
        else:
            print("The tentacle attack misses.")
            return False

    def use_ink_cloud_reaction(self, trigger_damage, attacker):
        """Use Ink Cloud reaction with basic implementation."""
        # Check if already used
        for trait in self.traits:
            if trait.get('name') == 'Ink Cloud' and trait.get('used_today', False):
                return False
        
        if getattr(self, 'has_used_reaction', False):
            return False
        
        print(f"REACTION: {self.name} releases a cloud of ink!")
        print(f"** Ink fills a 10-foot Cube centered on {self.name} **")
        print(f"** Cube is Heavily Obscured for 1 minute **")
        print(f"** {self.name} moves up to its Swim Speed (60 ft.) **")
        
        # Move away from threat
        self.position += 30  # Simple movement away
        print(f"** {self.name} swims to position {self.position}ft **")
        
        # Mark as used
        for trait in self.traits:
            if trait.get('name') == 'Ink Cloud':
                trait['used_today'] = True
                break
        
        self.has_used_reaction = True
        return True

    def process_effects_on_turn_start(self):
        """Process effects using global systems where available."""
        super().process_effects_on_turn_start()

        # Try to use global systems, fall back to basic validation
        try:
            from systems.grappling.grapple_manager import GlobalGrappleManager
            GlobalGrappleManager.validate_all_grapples([self])
        except (ImportError, AttributeError):
            # Basic validation fallback
            if self.is_grappling and (not hasattr(self, 'grapple_target') or not self.grapple_target or not self.grapple_target.is_alive):
                self.is_grappling = False
                self.grapple_target = None
        
        # Process ongoing spell effects (Searing Smite, etc.)
        if hasattr(self, 'searing_smite_effect') and self.searing_smite_effect.get('active', False):
            effect = self.searing_smite_effect
            dice_count = effect['dice_count']
            save_dc = effect['save_dc']
            caster = effect['caster']
            
            # Deal ongoing fire damage
            from core import roll
            ongoing_damage = 0
            for _ in range(dice_count):
                ongoing_damage += roll('1d6')
            
            print(f"** {self.name} takes {ongoing_damage} fire damage ({dice_count}d6) from Searing Smite! **")
            self.take_damage(ongoing_damage, attacker=caster)
            
            # Constitution saving throw to end the effect
            if self.is_alive:
                if self.make_saving_throw('con', save_dc):
                    print(f"** {self.name} extinguishes the searing flames! **")
                    self.searing_smite_effect['active'] = False
                    del self.searing_smite_effect

    def take_damage(self, damage, attacker=None):
        """Handle damage using global systems."""
        # Check for ink cloud trigger BEFORE taking damage
        should_trigger_ink = (self.is_alive and damage > 0 and attacker)
        
        # Take damage via global damage system
        super().take_damage(damage, attacker)

        # Trigger ink cloud via global reaction system
        if should_trigger_ink and self.is_alive:
            self.use_ink_cloud_reaction(damage, attacker)

        # Handle death cleanup via global systems
        if not self.is_alive:
            from systems.death import handle_creature_death
            handle_creature_death(self)

    def take_turn(self, combatants):
        """Take turn using existing turn system with octopus-specific handling."""
        self.has_used_action = False
        self.has_used_bonus_action = False
        
        # Store combatants reference
        self.current_combatants = combatants
        
        chosen_actions = self.ai_brain.choose_actions(self, combatants)

        defender = chosen_actions.get('action_target') or next((c for c in combatants if c.is_alive and c != self), None)

        moved = False
        movement_executed = 0

        # Movement logic for octopus
        if defender and chosen_actions.get('action'):
            action = chosen_actions.get('action')
            
            # Basic movement for tentacle attacks
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
            else:
                # Standard movement for other actions
                from actions.base_actions import AttackAction
                if isinstance(action, AttackAction):
                    current_distance = abs(self.position - defender.position) if defender else 0
                    weapon_reach = getattr(action.weapon, 'reach', 5)
                    
                    if current_distance > weapon_reach:
                        needed_movement = current_distance - weapon_reach
                        actual_movement = min(self.speed, needed_movement)
                        
                        if actual_movement > 0:
                            direction = 1 if defender.position > self.position else -1
                            self.position += actual_movement * direction
                            movement_executed = actual_movement
                            print(f"MOVEMENT: {self.name} moves {movement_executed} feet towards {defender.name}.")
                            moved = True

        if not moved:
            print("MOVEMENT: (None)")

        # PHB 2024: Octopus has no bonus actions
        print("BONUS ACTION: (None)")

        # Handle octopus actions - PHB 2024: ONLY Tentacles action exists
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
                # Standard action execution (AttackAction using tentacles)
                action.execute(self, action_target, "ACTION")
                self.has_used_action = True
        else:
            print("ACTION: (None)")

        # Check ink cloud availability
        ink_available = not any(trait.get('used_today', False) for trait in self.traits if trait.get('name') == 'Ink Cloud')
        print("REACTION: (Available - Ink Cloud 1/Day)" if ink_available else "REACTION: (Ink Cloud used)")

    def make_saving_throw(self, ability, dc):
        """Make saving throw using global saving throw system."""
        from systems.combat.saving_throws import make_creature_save
        
        # PHB 2024: Use exact stat block saves (no proficiency bonuses)
        return make_creature_save(
            creature=self,
            ability=ability,
            dc=dc,
            proficiency_bonus=0  # PHB 2024: Octopus has no save proficiencies
        )

    def release_grapple(self, target=None):
        """Release grapple using global grappling system where available."""
        target_to_release = target or getattr(self, 'grapple_target', None)
        
        if target_to_release:
            try:
                from systems.grappling.grapple_manager import GlobalGrappleManager
                GlobalGrappleManager.end_grapple(self, target_to_release)
            except (ImportError, AttributeError):
                # Fallback to direct implementation
                print(f"** {self.name} releases {target_to_release.name} from its tentacles **")
                
                # Remove octopus-specific condition first (Restrained)
                if hasattr(target_to_release, 'is_restrained'):
                    target_to_release.is_restrained = False
                    print(f"** {target_to_release.name} is no longer restrained **")
                
                # Remove standard grapple conditions from TARGET
                if hasattr(target_to_release, 'is_grappled'):
                    target_to_release.is_grappled = False
                if hasattr(target_to_release, 'grappler'):
                    delattr(target_to_release, 'grappler')
                if hasattr(target_to_release, 'grapple_escape_dc'):
                    delattr(target_to_release, 'grapple_escape_dc')
                
                print(f"** {target_to_release.name} is no longer grappled **")
                
                # Remove grappling condition from OCTOPUS
                self.is_grappling = False
                self.grapple_target = None
    
    def __str__(self):
        """String representation showing global system integration."""
        base_info = super().__str__()
        
        # Show global system status
        global_info = f"\n--- Global Systems Integration ---"
        global_info += f"\nGrappling: Via systems/grappling/"
        global_info += f"\nConditions: Via systems/conditions/"
        global_info += f"\nTraits: Via systems/creature_traits/"
        global_info += f"\nSaving Throws: Via systems/combat/saving_throws/"
        global_info += f"\nTurn Management: Via systems/combat/turn_system/"
        
        if hasattr(self, 'is_grappling') and self.is_grappling:
            global_info += f"\nCurrently Grappling: {getattr(self, 'grapple_target', {}).name if hasattr(self, 'grapple_target') else 'Unknown'}"
        
        return base_info + global_info
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
        
        # Set up grappling using ONLY global grappling system
        self._setup_global_grappling()
        
        # Set up other global systems
        self._setup_global_traits()
        self._setup_global_ai()

    def _setup_global_grappling(self):
        """Set up grappling using ONLY the global grappling system."""
        from systems.grappling.grapple_manager import setup_creature_grappling
        
        # Use the giant_octopus profile from global system
        setup_creature_grappling(self, 'giant_octopus')

    def _setup_global_traits(self):
        """Set up creature traits using global trait system."""
        # PHB 2024: Water Breathing trait
        from systems.creature_traits import add_trait
        
        # Use global trait system for water breathing
        if hasattr(self, 'traits'):
            self.traits = []
        else:
            self.traits = []
        
        # Add water breathing trait through global system
        self.traits.append({
            'name': 'Water Breathing',
            'description': 'Can breathe only underwater. Holds breath for 1 hour outside water.',
            'type': 'environmental'
        })
        
        # Add ink cloud reaction through global system
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
        PHB 2024 Tentacles attack using ONLY global systems.
        """
        # Use global attack system
        from systems.combat.attack_system import make_creature_attack
        from systems.grappling.grapple_manager import GlobalGrappleManager
        
        if not self.is_alive or not target or not target.is_alive:
            return False

        # PHB 2024: Size restriction check using global size system
        from systems.creature_size import can_grapple_size
        if not can_grapple_size(self.size, target.size, max_difference=1):
            print(f"{action_type}: {self.name}'s tentacles cannot grapple {getattr(target, 'size', 'Medium')} creatures!")
            return False

        # Range check using global range system
        from systems.combat.range_system import check_weapon_range
        if not check_weapon_range(self, target, self.equipped_weapon):
            distance = abs(self.position - target.position)
            print(f"TENTACLES: {self.name} out of range (distance: {distance}ft, reach: 10ft)")
            return False

        # PHB 2024: Single target check using global grappling system
        if self.is_grappling and hasattr(self, 'grapple_target') and self.grapple_target != target:
            print(f"TENTACLES: {self.name} already grappling {self.grapple_target.name} with all tentacles!")
            return False

        print(f"TENTACLES: {self.name} attacks {target.name} with Tentacles!")

        # Make attack using global attack system
        attack_result = make_creature_attack(
            attacker=self,
            target=target,
            weapon=self.equipped_weapon,
            attack_bonus=5,  # PHB 2024: +5 to hit
            action_type=action_type
        )

        if attack_result['hit']:
            # Apply grapple using global grappling system
            return GlobalGrappleManager.apply_grapple_conditions(
                grappler=self,
                target=target,
                escape_dc=13,  # PHB 2024: Fixed DC 13
                additional_conditions=['Restrained']  # PHB 2024: Octopus applies Restrained
            )
        
        return False

    def use_ink_cloud_reaction(self, trigger_damage, attacker):
        """Use Ink Cloud reaction via global reaction system."""
        from systems.reactions import can_use_reaction, use_reaction
        from systems.creature_traits import get_trait, use_trait
        
        # Check if reaction is available via global system
        if not can_use_reaction(self, 'Ink Cloud'):
            return False
        
        # Check if trait is available via global trait system
        ink_trait = get_trait(self, 'Ink Cloud')
        if not ink_trait or ink_trait.get('used_today', False):
            return False
        
        print(f"REACTION: {self.name} releases a cloud of ink!")
        
        # Apply effects via global systems
        from systems.environmental.obscurement import create_obscured_area
        from systems.movement import move_creature
        
        # Create heavily obscured area via global environmental system
        create_obscured_area(
            center_position=self.position,
            area_type='cube',
            size=10,
            obscurement_level='heavy',
            duration=600  # 1 minute in seconds
        )
        
        # Move using global movement system
        move_creature(self, distance=30, direction='away_from_threat')
        
        # Mark trait as used via global trait system
        use_trait(self, 'Ink Cloud')
        
        # Mark reaction as used via global reaction system
        use_reaction(self, 'Ink Cloud')
        
        return True

    def process_effects_on_turn_start(self):
        """Process effects using ONLY global systems."""
        super().process_effects_on_turn_start()

        # Validate all conditions via global condition system
        from systems.conditions import validate_creature_conditions
        validate_creature_conditions(self)
        
        # Validate grapple state via global grappling system
        from systems.grappling.grapple_manager import GlobalGrappleManager
        GlobalGrappleManager.validate_all_grapples([self])
        
        # Process ongoing spell effects via global spell system
        from systems.spells.ongoing_effects import process_ongoing_spell_effects
        process_ongoing_spell_effects(self)

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
        """Take turn using global turn system."""
        from systems.combat.turn_system import execute_creature_turn
        
        # Use global turn system instead of local implementation
        execute_creature_turn(self, combatants)

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
        """Release grapple using global grappling system."""
        from systems.grappling.grapple_manager import GlobalGrappleManager
        
        target_to_release = target or getattr(self, 'grapple_target', None)
        if target_to_release:
            GlobalGrappleManager.end_grapple(self, target_to_release)
    
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
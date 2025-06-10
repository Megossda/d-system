# File: enemies/cr_2_5/giant_constrictor_snake.py
from ..base_enemy import Enemy
from equipment.weapons.base_weapon import Weapon
from ai.enemy_ai.beast.giant_constrictor_snake_ai import GiantConstrictorSnakeAI
from actions.special_actions import MultiattackAction
from actions.base_actions import AttackAction
from core import roll_d20, get_ability_modifier, roll


class GiantConstrictorSnake(Enemy):
    """A Giant Constrictor Snake - CR 2 challenge with proper D&D 2024 rules."""

    def __init__(self, name="Giant Constrictor Snake", position=0):
        # Natural weapons for the snake
        snake_bite = Weapon(
            name="Bite",
            damage_dice="2d6",
            damage_type="Piercing",
            properties=['Reach'],  # 10ft reach
            reach=10
        )

        snake_constrict = Weapon(
            name="Constrict",
            damage_dice="2d8",
            damage_type="Bludgeoning",
            properties=['Grapple']  # Special grappling weapon
        )

        super().__init__(
            name=name,
            level=1,  # Minimal level for compatibility, but we override what matters
            hp=60,  # 8d12 + 8
            stats={'str': 19, 'dex': 14, 'con': 12, 'int': 1, 'wis': 10, 'cha': 3},
            weapon=snake_bite,
            armor=None,  # Natural AC
            shield=None,
            cr='2',  # This is what really matters for monsters
            position=position,
            initiative_bonus=0,
            speed=30
        )
        self.secondary_weapon = snake_constrict
        self.ai_brain = GiantConstrictorSnakeAI()
        self.size = 'Huge'
        self.is_grappling = False
        self.grapple_target = None

        # Add MultiattackAction to available actions
        self.available_actions.append(MultiattackAction(self))

    def calculate_ac(self):
        """Override AC calculation for natural armor"""
        return 12  # Natural armor from stat block
    
    def get_proficiency_bonus(self):
        """Override to use correct CR 2 proficiency bonus."""
        return 2  # CR 2 creatures have +2 proficiency bonus

    def multiattack(self, target, action_type="ACTION"):
        """Snake's multiattack: Bite + Constrict (PHB 2024 ranges)"""
        print(f"{action_type}: {self.name} uses Multiattack!")
        print(f"** Making a Bite attack and a Constrict attack **")

        # First attack: Bite (with 10ft reach)
        print(f"\n--- BITE ATTACK (Reach 10ft) ---")
        self.bite_attack(target)

        # Second attack: Constrict (10ft range, but only if not already grappling)
        if target.is_alive and abs(self.position - target.position) <= 10:
            if not self.is_grappling:
                print(f"\n--- CONSTRICT ATTACK (Range 10ft) ---")
                self.constrict_attack(target)
            else:
                print(f"\n--- Already grappling {self.grapple_target.name}, cannot constrict another target ---")
        else:
            print(f"\n--- Target too far for Constrict attack (needs 10ft range) ---")

    def bite_attack(self, target):
        """Bite attack with 10ft reach"""
        if not self.is_alive or not target or not target.is_alive:
            return

        # Check range (Bite has 10ft reach)
        distance = abs(self.position - target.position)
        if distance > 10:
            print(
                f"BITE: {self.name} tries to bite {target.name}, but is out of range (distance: {distance}ft, reach: 10ft)")
            return

        print(f"BITE: {self.name} attacks {target.name} (AC: {target.ac}) with Bite!")

        attack_roll, _ = roll_d20()
        attack_modifier = get_ability_modifier(self.stats['str'])
        prof_bonus = self.get_proficiency_bonus()
        total_attack = attack_roll + attack_modifier + prof_bonus

        print(f"ATTACK ROLL: {attack_roll} (1d20) +{attack_modifier} (STR) +{prof_bonus} (Prof) = {total_attack}")

        if total_attack >= target.ac or attack_roll == 20:
            is_crit = (attack_roll == 20)
            if is_crit:
                print(">>> CRITICAL HIT! <<<")
            else:
                print("The bite attack hits!")

            # Damage calculation
            damage = roll(self.equipped_weapon.damage_dice)
            if is_crit:
                crit_damage = roll(self.equipped_weapon.damage_dice)
                damage += crit_damage
                print(f"CRIT DAMAGE: Doubled dice from {self.equipped_weapon.damage_dice}")

            total_damage = damage + attack_modifier
            print(
                f"{self.name} deals {total_damage} piercing damage ({damage} [{self.equipped_weapon.damage_dice}{'+ crit' if is_crit else ''}] +{attack_modifier} [STR])")
            target.take_damage(total_damage, attacker=self)
        else:
            print("The bite attack misses.")

    def constrict_attack(self, target):
        """Constrict attack with grappling (10ft range) - PHB 2024 version with STR save."""
        if not self.is_alive or not target or not target.is_alive:
            return

        # Check range (Constrict has 10ft range in 2024)
        distance = abs(self.position - target.position)
        if distance > 10:
            print(
                f"CONSTRICT: {self.name} tries to constrict {target.name}, but is out of range (distance: {distance}ft, reach: 10ft)")
            return

        print(f"CONSTRICT: {self.name} attempts to constrict {target.name}!")
        print(f"** {target.name} must make a DC 14 Strength saving throw! **")

        # PHB 2024: Constrict uses a Strength saving throw, not an attack roll
        if target.make_saving_throw('str', 14):
            print(f"** {target.name} resists the constriction! **")
            return

        # Save failed - apply damage and grapple
        print(f"** {target.name} fails the saving throw! **")

        # Damage calculation
        damage = roll(self.secondary_weapon.damage_dice)
        total_damage = damage + get_ability_modifier(self.stats['str'])
        
        print(f"{self.name} deals {total_damage} bludgeoning damage ({damage} [{self.secondary_weapon.damage_dice}] +{get_ability_modifier(self.stats['str'])} [STR])")
        target.take_damage(total_damage, attacker=self)

        # Apply grapple effect properly (PHB 2024)
        if target.is_alive:
            # Set grapple state on both creatures
            self.is_grappling = True
            self.grapple_target = target
            target.is_grappled = True
            target.grappler = self
            
            # PHB 2024: Escape DC is 14 for Giant Constrictor Snake
            target.grapple_escape_dc = 14
            
            print(f"** {target.name} is GRAPPLED by the snake! **")
            print(f"** {target.name} has the Grappled condition: Speed 0, disadvantage on attacks vs others **")
            print(f"** Escape DC: 14 (STR Athletics or DEX Acrobatics check) **")
            print(f"** The snake can choose to crush {target.name} (using its action) instead of multiattack! **")  

    def crush_grappled_target(self, action_type="ACTION"):
        """OPTIMAL: Use action to deal guaranteed Constrict damage to grappled target."""
        if not self.is_grappling or not self.grapple_target or not self.grapple_target.is_alive:
            print(f"{action_type}: {self.name} has no target to crush!")
            return False
        
        target = self.grapple_target
        print(f"{action_type}: {self.name} crushes {target.name} with its coils!")
        
        # GUARANTEED DAMAGE: When crushing an already-grappled target, no save required
        damage = roll(self.secondary_weapon.damage_dice)
        total_damage = damage + get_ability_modifier(self.stats['str'])
        
        print(f"{self.name} deals {total_damage} bludgeoning damage ({damage} [{self.secondary_weapon.damage_dice}] +{get_ability_modifier(self.stats['str'])} [STR]) - GUARANTEED")
        target.take_damage(total_damage, attacker=self)
        
        print(f"** {target.name} remains grappled and can attempt to escape on their turn! **")
        return True

    def take_turn(self, combatants):
        """Override take_turn to handle optimal crush action."""
        self.has_used_action = False
        self.has_used_bonus_action = False
        
        # Store combatants reference for grapple system
        self.current_combatants = combatants
        
        chosen_actions = self.ai_brain.choose_actions(self, combatants)

        defender = chosen_actions.get('action_target') or next((c for c in combatants if c.is_alive and c != self), None)

        moved = False
        movement_executed = 0

        # Normal movement logic (snakes aren't grappled by default)
        if defender and chosen_actions.get('action'):
            action = chosen_actions.get('action')
            
            # Get movement recommendation from range manager if available
            if hasattr(self, 'ai_brain') and hasattr(self.ai_brain, 'last_tactical_recommendation'):
                tactical_rec = self.ai_brain.last_tactical_recommendation
                if tactical_rec and tactical_rec.get('movement_needed', 0) > 0:
                    recommended_movement = min(self.speed, tactical_rec['movement_needed'])
                    if recommended_movement > 0:
                        direction = 1 if defender.position > self.position else -1
                        self.position += recommended_movement * direction
                        movement_executed = recommended_movement
                        print(f"MOVEMENT: {self.name} moves {movement_executed} feet towards {defender.name}.")
                        moved = True

            # Fallback: Original movement logic for attacks
            if not moved and isinstance(action, AttackAction):
                weapon = action.weapon
                is_ranged = hasattr(weapon, 'properties') and 'Ranged' in weapon.properties
                
                if not is_ranged:
                    # For multiattack, check what ranges we need
                    if hasattr(action, 'action') and hasattr(action.action, 'creature'):
                        # This is a multiattack action
                        current_distance = abs(self.position - defender.position)
                        
                        # For snake multiattack: both Bite (10ft) and Constrict (10ft) need 10ft range
                        if current_distance > 10:
                            needed_movement = current_distance - 10
                            actual_movement = min(self.speed, needed_movement)
                            
                            if actual_movement > 0:
                                direction = 1 if defender.position > self.position else -1
                                self.position += actual_movement * direction
                                movement_executed = actual_movement
                                print(f"MOVEMENT: {self.name} moves {movement_executed} feet towards {defender.name} (multiattack positioning).")
                                moved = True
                    else:
                        # Regular weapon attack movement
                        weapon_reach = getattr(weapon, 'reach', 5)
                        current_distance = abs(self.position - defender.position)
                        
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

        # Store movement info for tactical AI
        if hasattr(self, 'ai_brain'):
            self.ai_brain.last_movement_executed = movement_executed

        bonus_action = chosen_actions.get('bonus_action')
        if bonus_action and not self.has_used_bonus_action:
            bonus_target = chosen_actions.get('bonus_action_target')
            bonus_action.execute(self, bonus_target, "BONUS ACTION")
            self.has_used_bonus_action = True
        else:
            print("BONUS ACTION: (None)")

        action = chosen_actions.get('action')
        if action and not self.has_used_action:
            action_target = chosen_actions.get('action_target')
            
            # OPTIMAL HANDLING: Check if AI wants to crush grappled target
            if isinstance(action, str) and action == 'crush_grappled_target':
                # Special action: crush the grappled target for guaranteed damage
                success = self.crush_grappled_target("ACTION")
                if success:
                    self.has_used_action = True
            else:
                # Normal action execution
                action.execute(self, action_target, "ACTION")
                self.has_used_action = True
        else:
            print("ACTION: (None)")

        print("REACTION: (Not used)")

    def process_effects_on_turn_start(self):
        """Process ongoing spell effects at start of turn - NO automatic crush damage."""
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

        # Check if grappled target is still alive and valid
        if self.is_grappling and (not self.grapple_target or not self.grapple_target.is_alive):
            print(f"** {self.name} releases its grapple (target no longer valid) **")
            self.is_grappling = False
            self.grapple_target = None

    def take_damage(self, damage, attacker=None):
        """Override to handle grapple breaking on death"""
        super().take_damage(damage, attacker)

        # If the snake dies, release any grappled targets
        if not self.is_alive and self.is_grappling and self.grapple_target:
            print(f"** {self.grapple_target.name} is freed from the grapple! **")
            self.grapple_target.is_grappled = False
            if hasattr(self.grapple_target, 'grappler'):
                delattr(self.grapple_target, 'grappler')
            if hasattr(self.grapple_target, 'grapple_escape_dc'):
                delattr(self.grapple_target, 'grapple_escape_dc')
            self.is_grappling = False
            self.grapple_target = None
from spells.base_spell import Spell
from effects import SearingSmiteEffect
from core import roll


# --- 1st-Level Spells ---

class Bless(Spell):
    def __init__(self):
        super().__init__(name="Bless", level=1, school="Enchantment", requires_concentration=True)

    def cast(self, caster, target=None):
        # In a full implementation, this would affect multiple targets and add 1d4 to their attack rolls and saves.
        print(f"** {caster.name}'s allies feel divinely favored! **")
        caster.start_concentrating(self)
        return True


class Command(Spell):
    def __init__(self):
        super().__init__(name="Command", level=1, school="Enchantment")

    def cast(self, caster, target=None):
        # This spell would force a Wisdom save on a target to perform a one-word command.
        if target:
            print(f"** {caster.name} utters a divine command at {target.name}! **")
            # In a full implementation, we'd roll a save vs the caster's DC.
        return True


class CompelledDuel(Spell):
    def __init__(self):
        super().__init__(name="Compelled Duel", level=1, school="Enchantment", requires_concentration=True)

    def cast(self, caster, target=None):
        # This spell would force a Wisdom save on a target, compelling it to fight only the caster.
        if target:
            print(f"** {caster.name} compels {target.name} to a duel! **")
            caster.start_concentrating(self)
        return True


class CureWounds(Spell):
    def __init__(self):
        super().__init__(name="Cure Wounds", level=1, school="Abjuration")

    def cast(self, caster, target):
        if not target:
            return False

        healing_amount = roll('1d8') + caster.get_spellcasting_modifier()
        original_hp = target.hp
        target.hp = min(target.max_hp, target.hp + healing_amount)
        healed_for = target.hp - original_hp

        print(f"** {caster.name} heals {target.name} for {healed_for} HP! **")
        print(f"{target.name}'s HP is now {target.hp}/{target.max_hp}.")
        return True


class DivineFavor(Spell):
    def __init__(self):
        super().__init__(name="Divine Favor", level=1, school="Transmutation", requires_concentration=True)

    def cast(self, caster, target=None):
        # This spell would add 1d4 radiant damage to the caster's weapon attacks.
        print(f"** {caster.name}'s weapon glows with divine power! **")
        caster.start_concentrating(self)
        return True


class GuidingBolt(Spell):
    """The Guiding Bolt spell with FIXED advantage tracking."""

    def __init__(self):
        super().__init__(name="Guiding Bolt", level=1, school="Evocation", attack_save="Ranged", damage_type="Radiant")

    def cast(self, caster, target):
        """Hurls a bolt of light that deals damage and makes the target easier to hit."""
        if not target:
            return False

        is_hit = caster.make_spell_attack(target, self)
        if is_hit:
            damage = roll('4d6')
            print(f"** The {self.name} strikes {target.name} for {damage} {self.damage_type} damage! **")
            target.take_damage(damage, attacker=caster)

            if target.is_alive:
                # FIXED: Set advantage with proper expiration tracking
                target.grants_advantage_to_next_attacker = True
                target.advantage_expires_round = getattr(caster, 'current_round', 1) + 1  # Next round
                print(f"** {target.name} is shimmering with light, the next attack roll against it has Advantage. **")
        return True


class Heroism(Spell):
    """The Heroism spell."""

    def __init__(self):
        super().__init__(name="Heroism", level=1, school="Enchantment", requires_concentration=True)

    def cast(self, caster, target=None):
        """A creature you touch is imbued with bravery."""
        target_to_affect = target or caster
        print(f"** {target_to_affect.name} is imbued with bravery and feels heroic! **")
        # In a full implementation, this would grant temporary HP each round.
        caster.start_concentrating(self)
        return True


class SearingSmite(Spell):
    def __init__(self):
        super().__init__(name="Searing Smite", level=1, school="Evocation", casting_time="1 Bonus Action",
                         requires_concentration=True, damage_type="Fire")

    def cast(self, caster, target=None):
        caster.active_smites.append(self)
        if self.requires_concentration:
            caster.start_concentrating(self)
        return True


# --- Spell Instances ---
bless = Bless()
command = Command()
compelled_duel = CompelledDuel()
cure_wounds = CureWounds()
divine_favor = DivineFavor()
guiding_bolt = GuidingBolt()
heroism = Heroism()
searing_smite = SearingSmite()
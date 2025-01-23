# Object classes from AP that represent different types of options that you can create
from Options import FreeText, NumericOption, Toggle, DefaultOnToggle, Choice, TextChoice, Range, NamedRange, ItemSet

# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value



####################################################################
# NOTE: At the time that options are created, Manual has no concept of the multiworld or its own world.
#       Options are defined before the world is even created.
#
# Example of creating your own option:
#
#   class MakeThePlayerOP(Toggle):
#       """Should the player be overpowered? Probably not, but you can choose for this to do... something!"""
#       display_name = "Make me OP"
#
#   options["make_op"] = MakeThePlayerOP
#
#
# Then, to see if the option is set, you can call is_option_enabled or get_option_value.
#####################################################################


# To add an option, use the before_options_defined hook below and something like this:
#   options["total_characters_to_win_with"] = TotalCharactersToWinWith
#
#class TotalCharactersToWinWith(Range):
#    """Instead of having to beat the game with all characters, you can limit locations to a subset of character victory locations."""
#    display_name = "Number of characters to beat the game with before victory"
#    range_start = 10
#    range_end = 50
#    default = 50

class Goal(Choice):
    """Choose your victory condition.
    Defeat Kaos: Defeat Kaos...there's not much more to it
    All Levels Perfected: 
    """
    display_name = "Goal"
    defeat_kaos = 0
    all_levels_perfected = 1

class CharactersAsItems(Toggle):
    """Unlock skylanders individually instead of by element."""
    display_name = "Characters as Items"
    default = True

class ChallengesAsLocations(Toggle):
    """Add locations for Cali's heroic challenges."""
    display_name = "Challenges as Locations"
    default = False

class PerElementUpgrades(Toggle):
    """Upgrade items become per-element instead of universal. Adds about 50 items"""
    display_name = "Per-Character Upgrades"
    default = False

class EmpireOfIceAddon(Toggle):
    """Adds checks for the Empire of Ice adventure pack."""
    display_name = "Empire of Ice Pack"
    default = False

class PirateShipAddon(Toggle):
    """Adds checks for the Pirate Ship adventure pack."""
    display_name = "Pirate Ship Pack"
    default = False

class DarklightCryptAddon(Toggle):
    """Adds checks for the Darklight Crypt adventure pack."""
    display_name = "Darklight Crypt Pack"
    default = False

class DragonsPeakAddon(Toggle):
    """Adds checks for the Dragon's Peak adventure pack."""
    display_name = "Dragon's Peak Pack"
    default = False

class ActiveItems(Toggle):
    """Adds active items to generation logic. Will only add items from enabled adventure packs."""
    display_name = "Active Items"
    default = False

class EnableHardTraps(Toggle):
    """Allows hard traps to replace fillers (currently only Reset Character Trap)."""
    display_name = "Hard Traps"
    default = True

class CharactersToExclude(ItemSet):
    """
    Skylanders that will not be included in generation.
    Does nothing if CharactersAsItems is false.
    Warning: if you have less than eight skylanders (and at least one from each element), some locations will be
      unreachable, which will make All Levels Perfected and some Completionist checks impossible to achieve
    """
    display_name = "Characters to Exclude"
    verify_item_name = True

class WhitelistCharacters(Toggle):
    """
    Treat CharactersToExclude as a whitelist instead of a blacklist. 
    """
    display_name = "Whitelist Characters"
    default = False

# This is called before any manual options are defined, in case you want to define your own with a clean slate or let Manual define over them
def before_options_defined(options: dict) -> dict:
    options["goal"] = Goal
    options["characters_as_items"] = CharactersAsItems
    options["challenges_as_locations"] = ChallengesAsLocations
    options["per_element_upgrades"] = PerElementUpgrades
    options["include_empire"] = EmpireOfIceAddon
    options["include_ship"] = PirateShipAddon
    options["include_crypt"] = DarklightCryptAddon
    options["include_peak"] = DragonsPeakAddon
    options["active_items"] = ActiveItems
    options["hard_traps"] = EnableHardTraps
    options["characters_to_exclude"] = CharactersToExclude
    options["whitelist_characters"] = WhitelistCharacters
    return options

# This is called after any manual options are defined, in case you want to see what options are defined or want to modify the defined options
def after_options_defined(options: dict) -> dict:
    return options
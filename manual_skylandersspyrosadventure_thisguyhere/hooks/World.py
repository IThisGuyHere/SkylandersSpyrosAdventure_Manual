# Object classes from AP core, to represent an entire MultiWorld and this individual World that's part of it
from worlds.AutoWorld import World
from BaseClasses import MultiWorld, CollectionState, ItemClassification

# Object classes from Manual -- extending AP core -- representing items and locations that are used in generation
from ..Items import ManualItem
from ..Locations import ManualLocation

# Raw JSON data from the Manual apworld, respectively:
#          data/game.json, data/items.json, data/locations.json, data/regions.json
#
from ..Data import game_table, item_table, location_table, region_table

# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value, is_location_name_enabled, is_item_name_enabled

# calling logging.info("message") anywhere below in this file will output the message to both console and log file
import logging

########################################################################################
## Order of method calls when the world generates:
##    1. create_regions - Creates regions and locations
##    2. create_items - Creates the item pool
##    3. set_rules - Creates rules for accessing regions and locations
##    4. generate_basic - Runs any post item pool options, like place item/category
##    5. pre_fill - Creates the victory location
##
## The create_item method is used by plando and start_inventory settings to create an item from an item name.
## The fill_slot_data method will be used to send data to the Manual client for later use, like deathlink.
########################################################################################



# Use this function to change the valid filler items to be created to replace item links or starting items.
# Default value is the `filler_item_name` from game.json
def hook_get_filler_item_name(world: World, multiworld: MultiWorld, player: int) -> str | bool:
    return False

# Called before regions and locations are created. Not clear why you'd want this, but it's here. Victory location is included, but Victory event is not placed yet.
def before_create_regions(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after regions and locations are created, in case you want to see or modify that information. Victory location is included.
def after_create_regions(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to remove locations from the world
    locationNamesToRemove = [] # List of location names

    # Add your code here to calculate which locations to remove
        

    for region in multiworld.regions:
        if region.player == player:
            for location in list(region.locations):
                if location.name in locationNamesToRemove:
                    region.locations.remove(location)
    if hasattr(multiworld, "clear_location_cache"):
        multiworld.clear_location_cache()

    # in non-linear mode, we need to make the hub the new starting region and connect it to all chapters
    if not get_option_value(multiworld, player, "linear_mode"):
        chapters = []
        for region in multiworld.regions:
            if region.player == player and "Chapter" in region.name:
                region.set_exits([])
                chapters.append(region.name)
        manual = multiworld.get_region("Manual", player)
        manual.set_exits([])
        manual.add_exits(["Hub"])

        hub = multiworld.get_region("Hub", player)
        hub.add_exits(chapters)    

# The item pool before starting items are processed, in case you want to see the raw item pool at that stage
def before_create_items_starting(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:

    # Use this hook to remove items from the item pool
    itemNamesToRemove = [] # List of item names
    locationNamesToRemove = [] # List of location names

    # Add your code here to calculate which items to remove.
    #
    # Because multiple copies of an item can exist, you need to add an item name
    # to the list multiple times if you want to remove multiple copies of it.

    # if a character is not in the list and whitelist is enabled OR a character is in the list and whitelist is disabled, remove that item
    names_to_remove = get_option_value(multiworld, player, "characters_to_exclude")
    use_character_whitelist = get_option_value(multiworld, player, "whitelist_characters")
    challenges_enabled = get_option_value(multiworld, player, "challenges_as_locations")

    if use_character_whitelist and len(names_to_remove) < 8:
        raise Exception("Whitelist was enabled, but does not contain enough skylanders. For optimal results, please ensure that the whitelist " + 
                        "contains at least 8 skylanders and at least one from each element.")

    # need to first check if the item is in item_pool
    for item in item_table:
        #table_item = next(i for i in item_table if i["name"] == item.name)
        if "category" not in item or "Skylander" not in item.get("category") or not is_item_name_enabled(multiworld,player,item.get("name")):
            continue
        item_name = item.get("name")
        character_in_list = False
        #for char_name in names_to_remove:
        #    if item_name.casefold() == char_name.casefold():
        #        character_in_list = True
        #        break
        if item_name in names_to_remove:
            character_in_list = True

        if (use_character_whitelist ^ character_in_list):
            itemNamesToRemove.append(item_name)
            # get rid of heroic challenges for removed characters
            if (challenges_enabled):
                locationNamesToRemove.append(f"Heroic Challenge - {item_name}")

    if challenges_enabled:
        for region in multiworld.regions:
            if region.player == player:
                for location in list(region.locations):
                    if location.name in locationNamesToRemove:
                        region.locations.remove(location)
                        print(f"Successfully removed Heroic Challenge - {itemName}")   # debug
        if hasattr(multiworld, "clear_location_cache"):
            multiworld.clear_location_cache()

    for itemName in itemNamesToRemove:
        item = next(i for i in item_pool if i.name == itemName)
        item_pool.remove(item)
        print("Successfully removed " + itemName)   # debug

    return item_pool

# The item pool after starting items are processed but before filler is added, in case you want to see the raw item pool at that stage
def before_create_items_filler(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    # Use this hook to remove items from the item pool
    itemNamesToRemove = [] # List of item names

    # Add your code here to calculate which items to remove.
    #
    # Because multiple copies of an item can exist, you need to add an item name
    # to the list multiple times if you want to remove multiple copies of it.


    # if playing nonlinear mode, we need to place Core of Light Fragments in the chapter locations and remove any extras
    if not get_option_value(multiworld, player, "linear_mode"):

        extra_map_frags = (4 - get_option_value(multiworld, player, "include_empire") - 
                           get_option_value(multiworld, player, "include_ship") - 
                           get_option_value(multiworld, player, "include_crypt") - 
                           get_option_value(multiworld, player, "include_peak"))
        
        for i in range(extra_map_frags):
            itemNamesToRemove.append("Core of Light Fragment")

        for location in location_table:
            if "Level Completion" in location["category"] and is_location_name_enabled(multiworld,player,location["name"]): 
                level = multiworld.get_location(location["name"], player)
                item_to_place = next(i for i in item_pool if i.name == "Core of Light Fragment")
                level.place_locked_item(item_to_place)
                item_pool.remove(item_to_place)



    for itemName in itemNamesToRemove:
        item = next(i for i in item_pool if i.name == itemName)
        item_pool.remove(item)


    # since the traps are weight-based, trap and filler generation needs to be overridden here
    
    extras = len(multiworld.get_unfilled_locations(player=player)) - len(item_pool)

    if extras > 0:
        traps = [item["name"] for item in item_table if item.get("trap")]
        filler = [item["name"] for item in item_table if item.get("filler")]
        #filler.append(world.get_filler_item_name())    # not really necessary anymore
        trap_percent = get_option_value(multiworld, player, "filler_traps")
        if not traps:
            trap_percent = 0

        trap_count = extras * trap_percent // 100
        filler_count = extras - trap_count

        weights = []
            
        for trap in traps:
            option_name = trap.casefold().replace(" ","_") + "_weight"
            weights.append(get_option_value(multiworld,player,option_name))

        if sum(weights) == 0:
            logging.warning(f"{world.player_name} thought setting all trap weights to 0 would be funny. They won't be laughing for long.")
            weights[-1] = 1

        for _ in range(0, trap_count):
            extra_item = world.create_item(world.random.choices(traps,weights=weights)[0])
            item_pool.append(extra_item)

        for _ in range(0, filler_count):
            extra_item = world.create_item(world.random.choice(filler))
            item_pool.append(extra_item)

    return item_pool

    # Some other useful hook options:

    ## Place an item at a specific location
    # location = next(l for l in multiworld.get_unfilled_locations(player=player) if l.name == "Location Name")
    # item_to_place = next(i for i in item_pool if i.name == "Item Name")
    # location.place_locked_item(item_to_place)
    # item_pool.remove(item_to_place)

# The complete item pool prior to being set for generation is provided here, in case you want to make changes to it
def after_create_items(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    
    return item_pool

# Called before rules for accessing regions and locations are created. Not clear why you'd want this, but it's here.
def before_set_rules(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after rules for accessing regions and locations are created, in case you want to see or modify that information.
def after_set_rules(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to modify the access rules for a given location

    def Example_Rule(state: CollectionState) -> bool:
        # Calculated rules take a CollectionState object and return a boolean
        # True if the player can access the location
        # CollectionState is defined in BaseClasses
        return True

    ## Common functions:
    # location = world.get_location(location_name, player)
    # location.access_rule = Example_Rule

    ## Combine rules:
    # old_rule = location.access_rule
    # location.access_rule = lambda state: old_rule(state) and Example_Rule(state)
    # OR
    # location.access_rule = lambda state: old_rule(state) or Example_Rule(state)

# The item name to create is provided before the item is created, in case you want to make changes to it
def before_create_item(item_name: str, world: World, multiworld: MultiWorld, player: int) -> str:
    return item_name

# The item that was created is provided after creation, in case you want to modify the item
def after_create_item(item: ManualItem, world: World, multiworld: MultiWorld, player: int) -> ManualItem:
    return item

# This method is run towards the end of pre-generation, before the place_item options have been handled and before AP generation occurs
def before_generate_basic(world: World, multiworld: MultiWorld, player: int) -> list:
    pass

# This method is run at the very end of pre-generation, once the place_item options have been handled and before AP generation occurs
def after_generate_basic(world: World, multiworld: MultiWorld, player: int):
    pass

# This is called before slot data is set and provides an empty dict ({}), in case you want to modify it before Manual does
def before_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called after slot data is set and provides the slot data at the time, in case you want to check and modify it after Manual is done with it
def after_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called right at the end, in case you want to write stuff to the spoiler log
def before_write_spoiler(world: World, multiworld: MultiWorld, spoiler_handle) -> None:
    pass

# This is called when you want to add information to the hint text
def before_extend_hint_information(hint_data: dict[int, dict[int, str]], world: World, multiworld: MultiWorld, player: int) -> None:
    
    ### Example way to use this hook: 
    # if player not in hint_data:
    #     hint_data.update({player: {}})
    # for location in multiworld.get_locations(player):
    #     if not location.address:
    #         continue
    #
    #     use this section to calculate the hint string
    #
    #     hint_data[player][location.address] = hint_string
    
    pass

def after_extend_hint_information(hint_data: dict[int, dict[int, str]], world: World, multiworld: MultiWorld, player: int) -> None:
    pass

from data.modules.services.spr_manager import spr_manager

from ..item import *

def load_items():

    tiles = spr_manager("data/sprites/items_sheet.png")

    #########
    # ITEMS #
    #########

    # Harvestable items

    wood = item(
        "wood", 0, 0, 32, (0, 0, 0),
        tiles.get_sprite(0, 0, 32, 32),
        0
    )

    stone = item(
        "stone", 0, 0, 32, (0, 0, 0),
        tiles.get_sprite(32, 0, 32, 32),
        0
    )

    sand = item(
        "sand", 0, 0, 32, (0, 0, 0),
        tiles.get_sprite(32*2, 0, 32, 32),
        0
    )

    coal = item(
        "coal", 0, 0, 32, (0, 0, 0),
        tiles.get_sprite(32*3, 0, 32, 32),
        0
    )

    copper_ore = item(
        "copper-ore", 0, 0, 32, (0, 0, 0),
        tiles.get_sprite(32*4, 0, 32, 32),
        0
    )

    # Tools

    stonepickaxe = stone_pickaxe(
        "arbol", 0, 0, 32, (0, 0, 0), 1, 32,
        tiles.get_sprite(0, 32*5, 32, 32)
    )

    stoneaxe = stone_axe(
        "mineral", 0, 0, 32, (0, 0, 0), 1, 32,
        tiles.get_sprite(32, 32*5, 32, 32)
    )

    stonesword = stone_sword(
        "bush", 0, 0, 32, (0, 0, 0), 7, 32,
        tiles.get_sprite(32*2, 32*5, 32, 32)
    )

    return {
        "wood": wood,
        "sand": sand,
        "stone": stone,
        "coal": coal,
        "copper-ore": copper_ore,
        "stone-pickaxe": stonepickaxe,
        "stone-axe": stoneaxe,
        "stone-sword": stonesword
    }
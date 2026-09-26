from data.modules.services.spr_manager import spr_manager
from ..block import *
from ..item import *
from .items import *


def load_blocks():

    tiles = spr_manager("data/sprites/tile_sheet.png")
    items = load_items()
    
    oak_tree1 = tree(
        "oak-tree", 0, 0, (0, 0, 0),
        tiles.get_sprite(0, 32*3 + 64*2, 128, 128),
        10, stone_axe,
        [(items.get("wood"), 2, 5)]
    )

    oak_tree2 = tree(
        "oak-tree", 0, 0, (0, 0, 0),
        tiles.get_sprite(128*4, 32*3 + 64*2, 128, 128),
        10, stone_axe,
        [(items.get("wood"), 2, 5)]
    )

    stone_chunk = mineral(
        "stone-chunk", 0, 0, (0, 0, 0),
        tiles.get_sprite(0, 32*3, 64, 64),
        5, stone_pickaxe,
        [(items.get("stone"), 2, 5)]
    )

    coal_chunk = mineral(
        "coal-chunk", 0, 0, (0, 0, 0),
        tiles.get_sprite(64, 32*3, 64, 64),
        5, stone_pickaxe,
        [(items.get("coal"), 2, 5)]
    )

    copper_chunk = mineral(
        "copper-chunk", 0, 0, (0, 0, 0),
        tiles.get_sprite(64*2, 32*3, 64, 64),
        5, stone_pickaxe,
        [(items.get("copper-ore"), 2, 5)]
    )

    sunflower = bush(
        "bush", 0, 0, (0, 0, 0),
        tiles.get_sprite(0, 32*2, 32, 32),
        1,
        drops=[(items.get("wood"), 2, 5)]
    )

    fungus = bush(
        "bush", 0, 0, (0, 0, 0),
        tiles.get_sprite(32, 32*2, 32, 32),
        1,
        drops=[(items.get("wood"), 2, 5)]
    )

    return {
        "oak-tree-1": oak_tree1,
        "oak-tree-2": oak_tree2,
        "stone-chunk": stone_chunk,
        "coal-chunk": coal_chunk,
        "copper-chunk": copper_chunk,
        "sunflower": sunflower,
        "fungus": fungus
    }
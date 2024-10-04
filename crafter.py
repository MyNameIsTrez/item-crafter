from enum import Enum, auto
from functools import cache
from math import ceil, inf


class Item(Enum):
    STICK = auto()
    PLANK = auto()
    OAK_LOG = auto()
    RUBBER_LOG = auto()
    IRON_INGOT = auto()
    IRON_BLOCK = auto()
    TRICKY = auto()


class Recipe:
    def __init__(self, items_per_craft, ingredients):
        self.items_per_craft = items_per_craft
        self.ingredients = ingredients


def get_recipes_producing_item(item: Item):
    return {
        Item.STICK: (
            Recipe(4, ((Item.PLANK, 2),)),
            Recipe(8, ((Item.RUBBER_LOG, 1),)),
        ),
        Item.PLANK: (Recipe(4, ((Item.OAK_LOG, 1),)),),
        Item.OAK_LOG: (),
        Item.RUBBER_LOG: (),
        Item.IRON_INGOT: (Recipe(9, ((Item.IRON_BLOCK, 1),)),),
        Item.IRON_BLOCK: (Recipe(1, ((Item.IRON_INGOT, 9),)),),
        Item.TRICKY: (Recipe(1, ((Item.STICK, 1), (Item.OAK_LOG, 1))),),
    }[item]


def immutable_dict(d: dict):
    return frozenset(d.items())


# @cache  # TODO: Try using this
def take(item: Item, count: int, storage: frozenset):
    params = (item, count, storage)
    if params in seen_params:
        return 0, storage  # Stops iron ingot -> iron block -> iron ingot loop
    seen_params.add(params)
    storage = dict(storage)
    returned_count = 0
    if item in storage:
        stored = storage[item]
        if stored >= count:
            storage[item] -= count
            return count, storage
        storage[item] -= stored
        count -= stored
        returned_count = stored
    possible_recipe_crafts = {}
    for recipe in get_recipes_producing_item(item):
        crafts_upper = ceil(count / recipe.items_per_craft)
        crafts = inf
        for ingredient, ingredient_count in recipe.ingredients:
            took, new_storage = take(
                ingredient, crafts_upper * ingredient_count, immutable_dict(storage)
            )
            crafts = min(crafts, took // ingredient_count)
        possible_recipe_crafts[recipe] = crafts
    # TODO: Try every permutation of recipes with varying craft counts
    return returned_count, storage


def test(
    item: Item,
    expected_count: int,
    storage: frozenset,
    expected_storage: frozenset,
):
    global seen_params
    seen_params = set()
    count, storage = take(item, expected_count, storage)
    assert count == expected_count
    assert storage == expected_storage


def test_sticks_from_planks_from_log():
    test(
        Item.STICK,
        1,
        immutable_dict({Item.OAK_LOG: 1}),
        immutable_dict({Item.STICK: 3, Item.PLANK: 2}),
    )


def test_iron_ingot_from_iron_block_infinite_loop():
    test(Item.IRON_INGOT, 1, immutable_dict({}), immutable_dict({}))


def test_sticks_from_planks_and_rubber_log():
    test(
        Item.STICK,
        12,
        immutable_dict({Item.OAK_LOG: 1, Item.RUBBER_LOG: 1}),
        immutable_dict({Item.PLANK: 2}),
    )


def test_requires_best_permutation():
    test(
        Item.TRICKY,
        1,
        immutable_dict({Item.OAK_LOG: 1, Item.RUBBER_LOG: 1}),
        immutable_dict({Item.STICK: 7}),
    )


def main():
    test_sticks_from_planks_from_log()
    test_iron_ingot_from_iron_block_infinite_loop()
    test_sticks_from_planks_and_rubber_log()
    test_requires_best_permutation()


if __name__ == "__main__":
    main()

import random
import CardCodec

from logic.Catalog import common_cards, uncommon_cards, rare_cards, legend_cards

# Random a full random pack of cards (4 cards common+, then 3 options for the last card)
def get_random_pack():
    pack = []
    for x in range(4):
        pack.append(get_random_pack_common_plus())

    # Get the remaining 3 choice cards
    pack += get_choice_cards()

    return pack


COMMON_IS_WILD_CHANCE = 1/4
def get_random_pack_common_plus():
    if random.random() <= COMMON_IS_WILD_CHANCE:
        return get_random_pack_wild()
    else:
        return random.choice(common_cards).id


# 2/3 to get unc, if not then 1/8 to get legend and 7/8 to get rare
UNCOMMON_CHANCE = 2/3
LEGEND_CHANCE = 1/8
def get_random_pack_wild():
    if random.random() <= UNCOMMON_CHANCE:
        pool = uncommon_cards
    elif random.random() <= LEGEND_CHANCE:
        pool = legend_cards
    else:
        pool = rare_cards

    return random.choice(pool).id

def get_choice_cards():
    if random.random() <= UNCOMMON_CHANCE:
        return map(lambda c: c.id, random.sample(uncommon_cards, 3))
    elif random.random() <= LEGEND_CHANCE:
        return map(lambda c: c.id, random.sample(legend_cards, 3))
    else:
        return map(lambda c: c.id, random.sample(rare_cards, 3))


print(get_random_pack())

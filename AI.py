from itertools import chain, combinations
import time

from logic.Effects import Status

# From itertools recipe
def powerset(l):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    return chain.from_iterable(combinations(l, r) for r in range(len(l)+1))

# The ai which, when enabled, will take all actions for the player

# For a given game state, decide what action to take (Card to play, or pass)
def get_action(model) -> int:
    time.sleep(.4)

    # Don't consider any of the restricted cards, which is the first X cards
    amt_restricted = model.status.count(Status.RESTRICTED)

    # Determine how to play cards such that the least mana is left over
    # Make a 2^6 bit number to represent which cards are considered, then check how close
    # that combination gets to spending all available mana
    high_score = 100
    best_possible = None
    for possible_turn in powerset(range(amt_restricted, len(model.hand))):
        total_cost = 0
        for card_num in possible_turn:
            total_cost += model.hand[card_num].cost

        score = model.mana - total_cost
        # Prefer playing more cards where possible
        # Can't spend more mana than we have
        if score >= 0:
            if score < high_score or score == high_score:# and len(possible_turn) > len(best_possible):
                high_score = score
                best_possible = possible_turn

    # If nothing can be played, pass
    if best_possible == ():
        return 10
    else:
        # The first card of the best possible turn (In terms of mana wasted)
        return best_possible[0]
    #
    # for index in range(6):
    #     if model.can_play(index):
    #         return index
    #
    # return 10

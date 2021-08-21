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
    time.sleep(.9)

    # If we've played points this round and opponent hasn't, don't play more
    opponent_has_played = False
    expected_points = 0
    for act in model.story.acts:
        if act.owner == 0:
            expected_points += act.card.points
        else:
            opponent_has_played = True

    if expected_points > 0 and not opponent_has_played:
        return 10

    # If we've played lots of points, stop
    if expected_points > model.max_mana[0] and len(model.hand) <= 4:
        return 10

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
            card = model.hand[card_num]

            cost = card.cost
            if card.name == 'Stalker':
                cost = model.opp_hand

            total_cost += cost

            # Some cards should only be played early
            if (card.name == 'Dash' or card.name == 'Factory' or card.name == 'Cosmos') and len(model.story.acts) > 1:
                total_cost -= 1000

        score = model.mana - total_cost
        # Prefer playing more cards where possible
        # Can't spend more mana than we have
        if score >= 0:
            if score < high_score or score == high_score:# and len(possible_turn) > len(best_possible):
                high_score = score
                best_possible = possible_turn

    # If nothing can be played, pass
    if best_possible == () or best_possible is None:
        return 10
    else:
        # Sort best_possible based on cost, to avoid swift, reset, and encourage playing finals last
        def get_cost(card):
            return model.hand[card].cost

        def uprising_last(x):
            card = model.hand[x]

            if card.name == 'Uprising':
                return 10
            else:
                return 1
        result = list(best_possible)
        result.sort(key=uprising_last)

        # The first card of the best possible turn (In terms of mana wasted)
        return result[0]
    #
    # for index in range(6):
    #     if model.can_play(index):
    #         return index
    #
    # return 10

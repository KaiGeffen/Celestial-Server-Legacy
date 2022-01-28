from itertools import chain, combinations
import time

from logic.Effects import Status, Quality


# From itertools recipe
def powerset(l):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    return chain.from_iterable(combinations(l, r) for r in range(len(l)+1))


# Return whether we know we are ahead in points
def know_we_are_ahead(model):
    our_points = 0
    their_points = 0

    our_nourish = model.status.count(Status.NOURISH) - model.status.count(Status.STARVE)
    their_nourish = model.opp_status.count(Status.NOURISH) - model.opp_status.count(Status.STARVE)

    for act in model.story.acts:
        if act.owner == 0:
            # Consume any nourish
            our_points += our_nourish
            our_nourish = 0

            # Add this act's expected points
            our_points += act.card.points
        else:
            # Consume any nourish
            their_points += their_nourish
            their_nourish = 0

            # Add this act's expected points only if we can see it
            if Quality.VISIBLE in act.card.qualities:
                their_points += act.card.points
    return our_points > their_points

# Return whether we would like to end the round 'dry' (With no cards played)
# By reacting to the opponent's pass with your own
# Thus ending the round with no plays (Dry round)
def want_dry_round(model):
    # Only consider drypassing if no cards have been played yet this round and opponent has passed
    if len(model.story.acts) > 0 or model.passes == 0:
        return False

    # Heuristic result, positive is good for us to drypass
    result = 0

    # Valuing each card drawn as worth 2 inspire

    # Consider how many cards we draw, and how many opponent draws
    we_draw = min(2, 6 - len(model.hand))
    result += 2 * we_draw
    they_draw = min(2, 6 - model.opp_hand)
    result -= 2 * they_draw

    # The amount of Inspired that will be lost, for us and them
    result -= model.status.count(Status.INSPIRED)
    result += model.opp_status.count(Status.INSPIRED)

    # TODO we have lesser discard pile triggers

    return result > 0

# The ai which, when enabled, will take all actions for the player

# For a given game state, decide what action to take (Card to play, or pass)
def get_action(model) -> int:
    time.sleep(.9)

    # If we know we've played more points than opponent, pass
    if know_we_are_ahead(model):
        return 10

    if want_dry_round(model):
        print('drypassing')
        return 10

    # Determine how to play cards such that the least mana is left over
    # Make a 2^6 bit number to represent which cards are considered, then check how close
    # that combination gets to spending all available mana
    high_score = 100
    best_possible = None
    for possible_turn in powerset(range(len(model.hand))):
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
        # Can't spend more mana than we have
        if score >= 0:
            if score < high_score or score == high_score:
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

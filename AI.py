from itertools import chain, combinations
import time
import copy

from logic.Effects import Status, Quality

# TODO Mulligan
# Don't play 2 resets in a row (Or separated by a card you play)

# From itertools recipe
def powerset(l):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    return chain.from_iterable(combinations(l, r) for r in range(len(l)+1))


# Return whether we know we are ahead in points
def predict_point_difference(model) -> int:
    our_points = 0
    their_points = 0

    our_nourish = model.status.count(Status.NOURISH) - model.status.count(Status.STARVE)
    their_nourish = model.opp_status.count(Status.NOURISH) - model.opp_status.count(Status.STARVE)

    their_mana = model.max_mana[0] + model.opp_status.count(Status.INSPIRED)
    they_played_hidden_cards = False

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
                their_mana -= act.card.cost
            else:
                they_played_hidden_cards = True

    # If they have played hidden cards, assume they spent all of their remaining mana
    # and got roughly that many points
    if they_played_hidden_cards:
        their_points += their_mana

    return our_points - their_points

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
    we_draw = min(2, 6 - len(model.hand), len(model.deck) + len(model.pile[0]))
    result += 2 * we_draw
    they_draw = min(2, 6 - model.opp_hand, model.opp_deck + len(model.pile[1]))
    result -= 2 * they_draw

    # The amount of Inspired that will be lost, for us and them
    result -= model.status.count(Status.INSPIRED)
    result += model.opp_status.count(Status.INSPIRED)

    # TODO we have lesser discard pile triggers

    return result > 0

# Try to play into our swift not theirs

# Rate the given turn based on a variety of heuristics
def rate_turn(turn, model):
    predicted_model = copy.deepcopy(model)

    remaining_mana = predicted_model.mana

    value = 0
    # Bonus for us/them based on the last card being a swift
    floating_swift_bonus = 0
    if len(model.story.acts) > 0:
        last_act = model.story.acts[-1]
        if last_act.card.name == 'Swift':
            if last_act.owner == 0:
                floating_swift_bonus = 1
            else:
                floating_swift_bonus = -1

    # Keep track of if the last card played gives a bonus for being played last
    final_card_bonus = 0

    for card_num in turn:
        card = predicted_model.hand[card_num]

        # Determine how much mana is left, if negative this is illegal
        remaining_mana -= predicted_model.costs[card_num]
        if remaining_mana < 0:
            return -1

        value += card.rate_play(predicted_model)

        # Predict this card being added TODO opponent plays?
        predicted_model.story.add_act(card, 0)

        # Special case for swift TODO name
        if card.cost == 1:
            value += floating_swift_bonus

        # if card.name == 'Swift':
        #     floating_swift_bonus = 1
        if card.name in ['Axolotl', 'Generator', 'Sun', 'Desert']:
            final_card_bonus = 1
        else:
            floating_swift_bonus = 0
            final_card_bonus = 0

    # Add a bonuses if final card benefits from being last
    value += final_card_bonus

    # Consider Nightmare TODO


    return value
    #
    # total_cost = 0
    # for card_num in possible_turn:
    #     card = model.hand[card_num]
    #
    #     cost = card.cost
    #     if card.name == 'Stalker':
    #         cost = model.opp_hand
    #
    #     total_cost += cost
    #
    #     # Some cards should only be played early
    #     if (card.name == 'Dash' or card.name == 'Factory' or card.name == 'Cosmos') and len(model.story.acts) > 1:
    #         total_cost -= 1000
    #
    # # Heuristics
    # # Mana efficient
    # score = model.mana - total_cost

# The ai which, when enabled, will take all actions for the player

# For a given game state, decide what action to take (Card to play, or pass)
def get_action(model) -> int:
    time.sleep(.9)

    # How many points up/down we believe we are
    point_difference = predict_point_difference(model)

    # If we know we've played more points than opponent, pass
    if point_difference > 0:
        return 10

    # If we can achieve a dry round and we want to, pass
    if want_dry_round(model):
        return 10

    # TODO Know I can't beat them

    # Determine how to play cards such that the least mana is left over
    # Make a 2^6 bit number to represent which cards are considered, then check how close
    # that combination gets to spending all available mana
    high_score = 0
    best_possible = None
    for possible_turn in powerset(range(len(model.hand))):
        score = rate_turn(possible_turn, model)

        # Can't spend more mana than we have
        if score > high_score:
            high_score = score
            best_possible = possible_turn

    # Determine if best_possible is enough to win
    # This assumes that the score is all going towards points
    # if high_score + point_difference <= 0:
    #     # TODO Play utility
    #     print(point_difference)
    #     return 10

    # If nothing can be played, pass
    if best_possible == () or best_possible is None:
        return 10
    else:
        # Sort best_possible such that cards that want to be played later are
        def sort_by_delay(i):
            return model.hand[i].rate_delay(model)
        l = list(best_possible)
        l.sort(key=sort_by_delay)
        return l[0]

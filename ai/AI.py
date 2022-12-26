import torch
from ai.Translator import translate_state
from ai.model import Linear_QNet
import CardCodec

# Load the model
# TODO dry + used in multiple threads
model = Linear_QNet(
    7 + 30 + 1 + 30*2 + 3 + 3 + 1, 256,
    1 + 59 + 4
    )
model.load()

PASS = -1

# For a given game state, decide what action to take
def get_action(client_state) -> int:
    state = torch.tensor(translate_state(client_state), dtype=torch.float)
    
    action = get_pass_or_id_action(state, client_state)

    # If action is to pass, return that
    if action == PASS:
        return PASS

    hand = CardCodec.decode_deck(client_state['hand'])
    for i in range(len(hand)):
        if hand[i].id == action:
            return i

    raise Exception('Get action returned an invalid action.')

# Get the id of each card that user can play
def get_valid_actions(client_state):
    # Passing is always allowed
    result = [PASS]

    hand = CardCodec.decode_deck(client_state['hand'])
    playable_list = client_state['cards_playable']
    for i in range(len(playable_list)):
        if playable_list[i]:
            card = hand[i]

            # Append the id of the card
            result.append(card.id)

    return result

# Return the suggested action as either PASS or the card's id
def get_pass_or_id_action(state, client_state):
    # Get valid actions we could take
    valid_actions = get_valid_actions(client_state)

    # Get the best prediction 
    state0 = torch.tensor(state, dtype=torch.float)
    prediction = model(state0)

    # Get the best options in order
    for best_choice in torch.argsort(prediction, descending=True):
        # Translate from the index in the vector to a card id or pass option

        # Choice to pass
        if best_choice == 0:
            return PASS
        else:
            # Otherwise translate choice to index within all cards
            # NOTE subtract 1 to account for pass being 0
            card = all_cards[best_choice - 1]   

            if card.id in valid_actions:
                return card.id



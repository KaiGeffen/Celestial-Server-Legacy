import pyglet

import CardCodec

# TODO arbitrary, think about
PASS = 10


class ClientModel(pyglet.event.EventDispatcher):
    # Supports now includes negative effects, called Traumas
    def __init__(self, state):
# hand, opp_hand, deck, opp_deck, pile, wins, max_mana, mana, supports, stack, priority, recap, version_num):
        super().__init__()

        self.hand = CardCodec.decode_deck(state['hand'])
        self.opp_hand = state['opp_hand']
        self.deck = CardCodec.decode_deck(state['deck'])
        self.opp_deck = state['opp_deck']
        self.pile = list(map(CardCodec.decode_deck, state['pile']))

        self.wins = state['wins']

        self.max_mana = state['max_mana']
        self.mana = state['mana']

        self.supports = state['supports']

        self.stack = CardCodec.decode_stack(state['stack'])
        # NOTE(kgeffen) Priority is relative: 0 means I have it, regardless of the id of my connection
        self.priority = state['priority']

        self.recap = CardCodec.decode_recap(state['recap'])

        self.version_num = state['version_num']

    # Return if the player can play the card
    def can_play(self, card_num):
        if not self.priority == 0:
            return False

        # Choice isn't in hand
        if card_num >= len(self.hand):
            return False

        card = self.hand[card_num]

        # Player doesn't have enough mana
        if card.cost > self.mana:
            return False

        return True

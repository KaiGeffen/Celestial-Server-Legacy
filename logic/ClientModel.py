import pyglet

import CardCodec

# TODO arbitrary, think about
PASS = 10


class ClientModel(pyglet.event.EventDispatcher):
    def __init__(self, state):
        super().__init__()

        self.hand = CardCodec.decode_deck(state['hand'])
        self.opp_hand = state['opp_hand']
        self.deck = CardCodec.decode_deck(state['deck'])
        self.opp_deck = state['opp_deck']
        self.pile = list(map(CardCodec.decode_deck, state['pile']))

        self.wins = state['wins']

        self.max_mana = state['max_mana']
        self.mana = state['mana']

        self.status = CardCodec.decode_statuses(state['status'])
        self.opp_status = CardCodec.decode_statuses(state['opp_status'])

        self.story = CardCodec.decode_story(state['story'])
        # NOTE(kgeffen) Priority is relative: 0 means I have it, regardless of the id of my connection
        self.priority = state['priority']

        self.passes = state['passes']

        self.recap = CardCodec.decode_recap(state['recap'])

        self.mulligans_complete = state['mulligans_complete']

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

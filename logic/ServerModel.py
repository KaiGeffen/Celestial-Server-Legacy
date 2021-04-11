import random

# from logic.ClientModel import ClientModel
import CardCodec
import SoundEffect
from logic.Catalog import hidden_card
from logic.Effects import Quality
from logic.Story import Story
from logic.Recap import Recap

DRAW_PER_TURN = 2
START_HAND = 3 - DRAW_PER_TURN
HAND_CAP = 6

MANA_GAIN_PER_TURN = 1
START_MANA = 1 - MANA_GAIN_PER_TURN
MANA_CAP = 10

# Input signifying user wants to pass
PASS = 10


class ServerModel:
    def __init__(self, deck1, deck2):
        super().__init__()

        self.hand = [[], []]
        self.deck = [deck1, deck2]
        self.pile = [[], []]
        for p in [0, 1]:
            self.shuffle(player=p, remember=False)
        # The last discard pile that each player was seen to shuffle back into their deck
        self.last_shuffle = [[], []]

        # Score in current round, and how many round wins
        self.score = [0, 0]
        self.wins = [0, 0]

        self.max_mana = [0, 0]
        self.mana = [0, 0]

        # The statuses the player is under
        self.status = [[], []]

        self.story = Story()
        self.passes = 0
        self.priority = 0

        # How many cards each player can see in the story this round
        self.vision = [0, 0]

        # Recap of the last round's resolution (Revealed stack + points awarded from each card)
        self.recap = self.story.recap

        # Whether each player has completed the mulligan phase at the start of the game
        self.mulligans_complete = [False, False]

        # The number of times an action has occured, used for syncing with clients
        self.version_no = 0

        # The sound effect for client's to play, based on the last action taken
        self.sound_effect = None

    """GENERIC ACTIONS"""
    # Player draws X cards from their deck
    def draw(self, player, amt=1):
        card = None

        # While not done drawing and hand has room for more cards
        while(amt > 0 and len(self.hand[player]) < HAND_CAP):

            # If deck is empty, shuffle in pile
            # If that's empty, stop drawing
            if(len(self.deck[player]) == 0):
                if(len(self.pile[player]) == 0):
                    return
                else:
                    self.shuffle(player)

            card = self.deck[player].pop()
            self.hand[player].append(card)

            amt -= 1

            self.sound_effect = SoundEffect.Draw

        return card

    def discard(self, player, amt=1, index=0):
        card = None
        while amt > 0 and len(self.hand[player]) > index:
            card = self.hand[player].pop(index)
            self.pile[player].append(card)

            amt -= 1

        if card is not None:
            self.sound_effect = SoundEffect.Discard

        return card

    def bottom(self, player, amt=1, index=0):
        card = None
        while amt > 0 and len(self.hand[player]) > index:
            card = self.hand[player].pop(index)
            self.deck[player].insert(0, card)

            amt -= 1

        return card

    # Shuffle X cards from player's hand into their deck
    def shuffle_into_deck(self, player, amt=1, index=0):
        card = None
        while amt > 0 and len(self.hand[player]) > index:
            card = self.hand[player].pop(index)
            self.deck[player].append(card)

            amt -= 1

        self.shuffle(player, remember=False)

        return card

    # Search through your deck, then your discard pile for a card with cost x. Draw that card
    def tutor(self, player, cost):
        if len(self.hand[player]) < HAND_CAP:

            for card in self.deck[player]:

                if card.cost == cost:
                    # Add it to hand, remove it from deck
                    self.hand[player].append(card)
                    self.deck[player].remove(card)

                    self.sound_effect = SoundEffect.Draw
                    return card

            for card in self.pile[player][::-1]:

                if card.cost == cost:
                    # Add it to hand, remove it from pile
                    self.hand[player].append(card)
                    self.pile[player].remove(card)

                    self.sound_effect = SoundEffect.Draw
                    return card

        return None

    # Create a copy of the given card in player's hand, if they have room
    def create(self, player, card):
        if len(self.hand[player]) < HAND_CAP:
            self.hand[player].append(card)

            self.sound_effect = SoundEffect.Create

            return card

        return None

    # Create a copy of the given card in player's pile
    def create_in_pile(self, player, card):
        self.pile[player].append(card)

    # Player cycles the given card, won't draw the same card, assumes card is in player's hand
    def cycle(self, player, card):
        self.hand[player].remove(card)
        drawn_card = self.draw(player)
        self.pile[player].append(card)

        return drawn_card

    # Remove from the game the card in your hand with the lowest cost, leftmost for tiebreaker
    def oust(self, player):
        cost = 0
        while len(self.hand[player]) > 0:
            for i in range(len(self.hand[player])):
                if self.hand[player][i].cost is cost:
                    card = self.hand[player][i]
                    del self.hand[player][i]
                    return card
            cost += 1

        return None

    # Move the top card of player's deck to the top of their pile
    def mill(self, player):
        if len(self.deck[player]) > 0:
            card = self.deck[player].pop()
            self.pile[player].append(card)
            return card

        return None

    # Counter the next card on the stack for which function returns true
    def counter(self, function):
        card = self.story.counter(function)
        return card

    # Shuffle the player's pile into their deck, optionally save the shuffled cards if they are known info
    def shuffle(self, player, remember=True):
        if remember:
            self.last_shuffle[player] = self.pile[player]

        self.deck[player] = self.pile[player] + self.deck[player]
        random.shuffle(self.deck[player])
        self.pile[player] = []

    # Create the given card in the player's hand, if possible
    def create_card(self, player, card):
        if len(self.hand[player]) < HAND_CAP:
            self.hand[player].append(card)

    """Generic UTILITY METHODS"""
    def get_highest_card_in_hand(self, player):
        result = None
        for card in self.hand[player]:
            if result is None or card.cost > result.cost:
                result = card

        return result

    """EXPOSED UTILITY METHODS"""

    def switch_priority(self):
        self.priority = (self.priority + 1) % 2

    # Get a model for the given player (So they see themselves as Player 1) also, sort the deck to hide ordering
    def get_client_model(self, player, cards_playable=[False]*6, total_vision=False):
        # How the deck is sorted (Cost, with same cards grouped) - used to sort player 1's deck below
        def deck_sort(card):
            rand_from_name = int.from_bytes(card.name.encode(), 'little') % 1000 / 1000
            return card.cost + rand_from_name

        # For player 1, don't reverse the lists, for player 2 do. This gives relative view of pile, wins, etc
        slice_step = 1 if player == 0 else -1
        relative_recap = self.recap if player == 0 else self.recap.get_flipped()

        return {
            'hand': CardCodec.encode_deck(self.hand[player]),
            'opp_hand': len(self.hand[player ^ 1]),
            'deck': CardCodec.encode_deck(sorted(self.deck[player], key=deck_sort)),
            'opp_deck': len(self.deck[player ^ 1]),
            'pile': list(map(CardCodec.encode_deck, self.pile[::slice_step])),
            'last_shuffle': list(map(CardCodec.encode_deck, self.last_shuffle[::slice_step])),
            'wins': self.wins[::slice_step],
            'max_mana': self.max_mana[::slice_step],
            'mana': self.mana[player],
            'status': CardCodec.encode_statuses(self.status[player]),
            'opp_status': CardCodec.encode_statuses(self.status[player ^ 1]),
            'story': self.get_relative_story(player, total_vision),
            'priority': self.priority ^ player,
            'passes': self.passes,
            'recap': CardCodec.encode_recap(relative_recap),
            'mulligans_complete': self.mulligans_complete[::slice_step],
            'version_num': self.version_no,
            'cards_playable': cards_playable,
            'vision': self.vision[player],
            'winner': None if self.get_winner() is None else self.get_winner() ^ player,
            'score': self.score[::slice_step],
            'sound_effect': self.sound_effect
        }

    # Get a view of the story that the given player can see
    def get_relative_story(self, player, total_vision):
        def hide_opponents_cards(live_card):
            card, owner = live_card
            if not total_vision and owner != player and Quality.VISIBLE not in card.qualities:
                return hidden_card, owner
            else:
                return live_card

        def switch_owners(live_card):
            card, owner = live_card
            return card, owner ^ 1

        # Add all acts to the story
        result = []
        for act in self.story.acts:
            result.append((act.card, act.owner))

        # Hide all of the opponent's acts that player can't see
        visible_result = result[0:self.vision[player]]
        invisible_result = list(map(hide_opponents_cards, result[self.vision[player]:]))
        result = visible_result + invisible_result

        if player == 1:
            result = list(map(switch_owners, result))

        return CardCodec.encode_story(result)

    """UTILITY CHECKS"""
    def get_winner(self):
        if self.wins[0] >= 5 and self.wins[0] >= self.wins[1] + 2:
            return 0

        if self.wins[1] >= 5 and self.wins[1] >= self.wins[0] + 2:
            return 1

        return None

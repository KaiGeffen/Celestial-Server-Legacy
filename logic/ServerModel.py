import pyglet
import random

# from logic.ClientModel import ClientModel
import CardCodec
from logic.Catalog import hidden_card
from logic.Effects import Quality

DRAW_PER_TURN = 2
START_HAND = 3 - DRAW_PER_TURN
HAND_CAP = 6

MANA_GAIN_PER_TURN = 1
START_MANA = 1 - MANA_GAIN_PER_TURN
MANA_CAP = 10

# Input signifying user wants to pass
PASS = 10


class ServerModel(pyglet.event.EventDispatcher):
    def __init__(self, deck1, deck2):
        super().__init__()

        self.hand = [[], []]
        self.deck = [[], []]
        self.pile = [deck1, deck2]

        # Score in current round, and how many round wins
        self.score = [0, 0]
        self.wins = [0, 0]

        self.max_mana = [0, 0]
        self.mana = [0, 0]

        # The statuses the player is under
        self.status = [[], []]

        self.stack = []
        self.passes = 0
        self.priority = 0

        # Bool for each player if they have total vision this round
        self.vision = [False, False]

        # Recap of the last round's resolution (Revealed stack + points awarded from each card)
        self.recap = Recap()

        # The number of times an action has occcured, used for syncing with clients
        self.version_no = 0

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

        return card

    def discard(self, player, amt=1, index=0):
        card = None
        while amt > 0 and len(self.hand[player]) > index:
            card = self.hand[player].pop(index)
            self.pile[player].append(card)

            amt -= 1

        return card

    # Search through your deck, then your discard pile for a card with cost x. Draw that card
    def tutor(self, player, cost):
        if len(self.hand[player]) < HAND_CAP:

            for card in self.deck[player]:

                if card.cost == cost:
                    # Add it to hand, remove it from deck
                    self.hand[player].append(card)
                    self.deck[player].remove(card)

                    return card

            for card in self.pile[player][::-1]:

                if card.cost == cost:
                    # Add it to hand, remove it from pile
                    self.hand[player].append(card)
                    self.pile[player].remove(card)

                    return card

        return None

    # Create a copy of the given card in player's hand, if they have room
    def create(self, player, card):
        if len(self.hand[player]) < HAND_CAP:
            self.hand[player].append(card)
            return card

        return None

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

    # Counter the next card on the stack
    def counter(self):
        if self.stack:
            (card, owner) = self.stack.pop(0)
            self.pile[owner].append(card)

            return card
        else:
            return None

    # Shuffle the player's pile into their deck
    def shuffle(self, player):
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
    def get_client_model(self, player):
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
            'wins': self.wins[::slice_step],
            'max_mana': self.max_mana[::slice_step],
            'mana': self.mana[player],
            'status': CardCodec.encode_statuses(self.status[player]),
            'opp_status': CardCodec.encode_statuses(self.status[player ^ 1]),
            'stack': self.get_relative_stack(player),
            'priority': self.priority ^ player,
            'recap': CardCodec.encode_recap(relative_recap),
            'version_num': self.version_no
        }

    # Get a view of the stack that the given player can see
    def get_relative_stack(self, player):
        def hide_opponents_cards(live_card):
            card, owner = live_card
            if owner != player and Quality.VISIBLE not in card.qualities:
                return hidden_card, owner
            else:
                return live_card

        def switch_owners(live_card):
            card, owner = live_card
            return (card, (owner + 1) % 2)

        result = self.stack
        if not self.vision[player]:
            result = list(map(hide_opponents_cards, result))

        if player == 1:
            result = list(map(switch_owners, result))

        return CardCodec.encode_stack(result)

    """UTILITY CHECKS"""
    def get_winner(self):
        return None

    def can_play(self, player, card_num):
        # Choice isn't in the player's hand
        if (card_num >= len(self.hand[player])):
            return False

        card = self.hand[player][card_num]

        # Player doesn't have enough mana
        if (card.cost > self.mana[player]):
            return False

        return True


class Recap():
    def __init__(self, stack=[], sums=[0,0], wins=[0,0]):
        self.stack = stack
        self.sums = sums
        self.wins = wins

    # In most cases, text is +N, but for things like RESET it could be different
    def add(self, card, owner, text):
        self.stack.append((card, owner, text))

    def add_total(self, sums, wins):
        self.sums[0] += sums[0]
        self.sums[1] += sums[1]

        self.wins[0] += wins[0]
        self.wins[1] += wins[1]

    def reset(self):
        self.stack = []
        self.sums = [0, 0]
        self.wins = [0, 0]

    # Return a flipped version of this recap
    def get_flipped(self):
        stack = []
        for (card, owner, text) in self.stack:
            stack.append((card, (owner + 1) % 2, text))

        sums = self.sums[::-1]
        wins = self.wins[::-1]

        return Recap(stack, sums, wins)

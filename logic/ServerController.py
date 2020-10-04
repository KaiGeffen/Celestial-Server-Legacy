import random

from logic.ServerModel import ServerModel

from logic import Catalog
from logic.Effects import Quality, Status
# TODO Separate out source
from logic.Story import Source


DRAW_PER_TURN = 2
START_HAND = 3 - DRAW_PER_TURN
HAND_CAP = 6

MANA_GAIN_PER_TURN = 1
START_MANA = 1 - MANA_GAIN_PER_TURN
MANA_CAP = 10

# Input signifying user wants to pass
PASS = 10


class ServerController():
    def __init__(self, deck1, deck2):
        self.model = ServerModel(deck1, deck2)

    # Return True if a play/pass occurred (False if play couldn't be completed)
    def on_player_input(self, player, choice):
        if player != self.model.priority:
            return False

        if choice == PASS:
            self.model.passes += 1

            self.model.switch_priority()

            # If both player's have passed in sequence, end turn and start another
            if self.model.passes == 2:
                self.do_takedown()
                self.model.passes = 0
                self.do_upkeep()

            self.model.version_no += 1
            return True
        else:
            if self.attempt_play(player, choice):
                self.model.passes = 0
                self.model.switch_priority()

                self.model.version_no += 1
                return True
            else:
                return False

    # Return false if given card couldn't be played
    def attempt_play(self, player, card_num):
        if self.can_play(player, card_num):
            self.play(player, card_num)
            return True
        else:
            print(f"Can't play the {card_num}th card")
            return False

    # Player puts the the nth card of their hand on the stack
    # Assumes that the card can be played
    def play(self, player, card_num):
        # Remove the card from hand, then play it
        card = self.model.hand[player].pop(card_num)

        self.model.mana[player] -= card.get_cost(player, self.model)

        card.on_play(player, self.model)

        self.model.story.add_act(card, owner=player, source=Source.HAND)

    """PHASES"""
    # Begin the game
    def start(self):
        self.do_setup()
        self.do_upkeep()

    # Perform the setup phase
    def do_setup(self):
        for player in (0, 1):
            self.model.draw(player, START_HAND)
            self.model.max_mana = [START_MANA, START_MANA]

    # Perform the upkeep phase
    def do_upkeep(self):
        self.model.vision = [False, False]

        # Give priority to the player in the lead, or random if tied
        if self.model.wins[0] > self.model.wins[1]:
            self.model.priority = 0
        elif self.model.wins[1] > self.model.wins[0]:
            self.model.priority = 1
        else:
            # TODO make deterministic?
            self.model.priority = random.choice([0, 1])

        # Each player draws, resets their mana, performs upkeep statuses, and card effects
        for player in (0, 1):
            self.model.draw(player, DRAW_PER_TURN)

            self.model.max_mana[player] += MANA_GAIN_PER_TURN
            if self.model.max_mana[player] > MANA_CAP:
                self.model.max_mana[player] = MANA_CAP
            self.model.mana[player] = self.model.max_mana[player]

            self.do_upkeep_statuses(player)

            # Each card in hand has a chance to do an upkeep effect
            for card in self.model.hand[player]:
                card.on_upkeep(player, self.model)

            # Each card in pile has a chance to do an upkeep effect
            for card in self.model.pile[player]:
                card.pile_upkeep(player, self.model)

    # Perform the takedown phase
    def do_takedown(self):

        # Resolve the story
        self.model.score = [0, 0]
        wins = [0, 0]

        # Reset to a new Recap for this round's takedown
        self.model.recap.reset()

        # Before the story is resolved, leftmost cards in player's hands can spring
        self.do_spring()

        self.model.story.run(self.model)

        #
        #
        # while self.model.story.do_act(self.model):
        #
        #
        # # The starting position of this card on the story
        # index = 0
        # while len(self.model.stack) > 0:
        #     card, player = self.model.stack.pop(0)
        #
        #     # Add the points from this card to the owner's points this round
        #     # Stack gets passed since it can influence how much a card is worth
        #     recap_text = card.play(player, self.model, index, 0)
        #     self.model.recap.add(card, player, recap_text)
        #
        #     # Put the spent card in players pile, unless it has Fleeting
        #     if Quality.FLEETING not in card.qualities:
        #         self.model.pile[player].append(card)
        #
        #     index += 1

        # Add to wins here
        if self.model.score[0] > self.model.score[1]:
            wins[0] += 1
        elif self.model.score[0] < self.model.score[1]:
            wins[1] += 1
        else:
            pass
        # Adjust the scores to reflect the wins from this round
        self.model.wins[0] += wins[0]
        self.model.wins[1] += wins[1]

        self.do_gentle()

        # Recap the results
        self.model.recap = self.model.story.recap
        self.model.recap.add_total(self.model.score, wins)

        self.model.story.clear()

    """EXPOSED UTILITY METHODS"""
    def get_client_model(self, player):
        return self.model.get_client_model(player)

    """SUB-PHASES"""
    def do_upkeep_statuses(self, player):

        # Clear Restricted first, so any added for this round aren't removed below
        self.model.status[player] = list(filter(Status.RESTRICTED.__ne__, self.model.status[player]))

        for stat in self.model.status[player]:

            # Flock : Add a bird to player's hand
            if stat is Status.FLOCK:
                self.model.create_card(player, Catalog.dove)

            # Boost : Gain 1 temporary mana
            if stat is Status.BOOST:
                self.model.mana[player] += 1

            # Restrict : Disallow played your leftmost card this round
            if stat is Status.RESTRICT:
                self.model.status[player].append(Status.RESTRICTED)

        cleared_statuses = [Status.BOOST,
                            Status.FLOCK,
                            Status.GENTLE,
                            Status.RESTRICT]

        def clear_temp_statuses(stat):
            return stat not in cleared_statuses
        self.model.status[player] = list(filter(clear_temp_statuses, self.model.status[player]))

    # The leftmost card in each player's hand, starting with priority player
    # may have an effect
    def do_spring(self):
        for player in (self.model.priority, (self.model.priority + 1) % 2):

            hand = self.model.hand[player]
            restricted = Status.RESTRICTED in self.model.status[player]

            if not restricted and len(hand) is not 0:
                if hand[0].spring:
                    self.model.story.add_act(hand[0], player, Source.SPRING)

                    # Remove the sprung card from hand
                    self.model.hand[player].pop(0)

    # If the winning player has gentle, award carryover equal to how much extra they won by
    def do_gentle(self):
        score_dif = self.model.score[0] - self.model.score[1]

        if score_dif > 0 and Status.GENTLE in self.model.status[0]:
            self.model.status[0].extend((score_dif - 1) * [Status.NOURISH])
        elif score_dif < 0 and Status.GENTLE in self.model.status[1]:
            self.model.status[1].extend((abs(score_dif) - 1) * [Status.NOURISH])

    """UTILITY CHECKS"""
    # Check if the given player can play the given card
    def can_play(self, player, card_num):
        # Choice isn't in the player's hand
        if card_num >= len(self.model.hand[player]):
            return False

        card = self.model.hand[player][card_num]

        # Player doesn't have enough mana
        if card.get_cost(player, self.model) > self.model.mana[player]:
            return False

        # Card is restricted by Restrict status
        if card_num + 1 <= self.model.status[player].count(Status.RESTRICTED):
            return False

        return True


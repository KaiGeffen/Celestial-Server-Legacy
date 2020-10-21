from logic.ServerController import ServerController
from logic.Catalog import get_computer_deck
from logic.ClientModel import ClientModel

import AI

# A mock version of the network for playing the game single-player locally against AI
class MockNetwork:
    def __init__(self, deck):
        opp_deck = get_computer_deck()

        self.game = ServerController(deck, opp_deck)
        self.game.start()

    def send_mulligans(self, mulligans):
        self.game.do_mulligan(0, mulligans)

        # Opponent must mulligan also
        self.game.do_mulligan(player=1, mulligans=[False, False, False])

        # Opponent acts, if they have priority it is the first play of the round
        if self.game.model.priority == 1:
            self.opponent_acts()

    # Ask the server for state
    # Include the version num of the state we have
    # So that if nothing has changed, we don't update
    def get_state(self, model):
        if model is None or model.version_num < self.game.model.version_no:
            return ClientModel(self.game.get_client_model(0))

    # Send the server an action that the user wishes to take, return true if action was valid
    def send_action(self, action):
        if action is not None:

            # Action was invalid
            if not self.game.on_player_input(0, action):
                return False

            # Action was performed and opponent now acts, then return True to signify that player action was valid
            else:
                self.opponent_acts()

                return True

    # Opponent plays cards until they don't have priority
    def opponent_acts(self):
        opponent_model = ClientModel(self.game.get_client_model(1))
        opponent_action = AI.get_action(opponent_model)

        self.game.on_player_input(1, opponent_action)

        # If my opponent still has priority, they act again
        if self.game.model.priority == 1:
            self.opponent_acts()

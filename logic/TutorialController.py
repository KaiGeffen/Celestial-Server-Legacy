from logic.ServerController import ServerController
from logic.ServerModel import ServerModel
from logic.Catalog import *

# TODO Dont mulligan
class TutorialController(ServerController):
    def __init__(self):
        # NOTE The last cards are the top of the deck, which isn't shuffled for tutorial
        player_deck = [dash, dove, dove, dove, gift, dash, dash, dash,
            dove, dove, dash, dove, dash, dove, dove]
        ai_deck = [drown, paranoia,
                   paranoia, drown, drown, drown, drown, drown, drown]
        self.model = ServerModel(player_deck, ai_deck, shuffle=False)

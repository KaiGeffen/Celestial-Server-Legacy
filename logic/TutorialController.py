from logic.ServerController import ServerController
from logic.Catalog import *


class TutorialController(ServerController):
    def __init__(self):
        player_deck = [dove, dove, dove, dove, dash, dash, dash]
        ai_deck = [drown, drown, drown, drown, drown, gift, gift]
        super().__init__(player_deck, ai_deck)

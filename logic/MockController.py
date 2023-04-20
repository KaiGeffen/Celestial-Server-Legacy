import unittest
from logic.ServerController import ServerController
from logic.Catalog import *


class MockController(ServerController):
    def __init__(self, deck1=[], deck2=[], skip_mulligan=True):
        super().__init__(deck1, deck2, 0, 0)

        self.start()

        # Set priority deterministically
        self.model.priority = 0

        if skip_mulligan:
            super().do_mulligan(0, (False, False, False, False))
            super().do_mulligan(1, (False, False, False, False))

    def on_player_input(self, player, choice, version=None):
        result = super().on_player_input(player, choice, version)
        if not result:
            print('Player input invalid!')


class TestMorning(unittest.TestCase):
    def test_nightmare(self):
        deck1 = [dove] * 15
        deck2 = [nightmare] * 15
        mock = MockController(deck1, deck2)
        model = mock.model

        # Round 1
        mock.on_player_input(0, 1)
        mock.on_player_input(1, 10)
        mock.on_player_input(0, 10)

        # Round 2
        mock.on_player_input(0, 1)
        mock.on_player_input(1, 1)
        mock.on_player_input(0, 1)
        mock.on_player_input(1, 10)
        mock.on_player_input(0, 10)

        # Assertions
        self.assertEqual(stalker, model.hand[1][4])


if __name__ == '__main__':
    unittest.main()

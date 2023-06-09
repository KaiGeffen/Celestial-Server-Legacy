import unittest
from logic.ServerController import ServerController
from logic.ServerModel import ServerModel
from logic.Catalog import *


class MockController(ServerController):
    def __init__(self, deck1=[], deck2=[], skip_mulligan=True):
        self.model = ServerModel(deck1, deck2, 0, 0, shuffle=False)

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

    def on_player_pass(self, player, version=None):
        self.on_player_input(player, 10, version)

    def set_unlimited_breath(self):
        for i in (0, 1):
            self.model.status[i].append(Status.UNLOCKED)
        # NOTE If these are 10 can't start round with a pass
        # self.model.max_mana = [100, 100]
        # self.model.mana = [100, 100]



class TestMorning(unittest.TestCase):
    def test_nightmare(self):
        deck1 = [dove] * 15
        deck2 = [nightmare] * 15
        mock = MockController(deck1, deck2)
        model = mock.model

        # Round 1
        mock.on_player_input(0, 1)
        mock.on_player_pass(1)
        mock.on_player_pass(0)

        # Round 2
        mock.on_player_input(0, 1)
        mock.on_player_input(1, 1)
        mock.on_player_input(0, 1)
        mock.on_player_pass(1)
        mock.on_player_pass(0)

        # Assertions
        self.assertEqual(stalker, model.hand[1][4])

class TestNourish(unittest.TestCase):
    def test_boa_negative(self):
        deck1 = [sine, symbiosis, sine]
        deck2 = [dove] * 15
        mock = MockController(deck1, deck2)
        model = mock.model
        mock.set_unlimited_breath()

        # Round 1 (Hungry Ghost, Boa)
        mock.on_player_input(0, 0)
        mock.on_player_pass(1)
        mock.on_player_input(0, 0)
        mock.on_player_pass(1)
        mock.on_player_pass(0)

        # Assertions
        self.assertEqual(4, len(model.hand[1]))

    # Test that if you gain equal parts nourish and starve it cancels
    def test_boa_nourish_cancels(self):
        deck1 = [symbiosis, dove, dove]
        deck2 = [sickness] * 15
        mock = MockController(deck1, deck2)
        model = mock.model
        mock.set_unlimited_breath()
        for _ in range(4):
            model.status[0].append(Status.NOURISH)

        # Round 1 (4 nourish, Sickness, Boa)
        mock.on_player_pass(0)
        mock.on_player_input(1, 0)
        mock.on_player_input(0, 0)
        mock.on_player_pass(1)
        mock.on_player_pass(0)

        # Assertions
        self.assertEqual(4, len(model.hand[1]))


if __name__ == '__main__':
    unittest.main()

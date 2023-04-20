import unittest
from logic.ServerController import ServerController
from logic.Catalog import *


class MockController(ServerController):
    def __init__(self, skip_mulligan=True):
        super().__init__([], [], 0, 0)

        # Set priority deterministically
        self.model.priority = 0

        if skip_mulligan:
            super().do_mulligan(0, (False, False, False, False))
            super().do_mulligan(1, (False, False, False, False))


class TestMorning(unittest.TestCase):
    def test_nightmare(self):
        mock = MockController()
        model = mock.model

        model.hand[1] = [dove]
        model.pile[1] = [nightmare]

        mock.on_player_input(0, 10)
        mock.on_player_input(1, 10)

        self.assertEqual(stalker, model.hand[1][1])


if __name__ == '__main__':
    unittest.main()

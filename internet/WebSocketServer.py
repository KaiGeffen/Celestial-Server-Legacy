import asyncio
import json
import logging
import websockets
import ssl
import pathlib
import os

from internet.Settings import *
import CardCodec
from logic.ServerController import ServerController
from logic.TutorialController import TutorialController
from logic.Catalog import get_computer_deck
from logic.ClientModel import ClientModel
import AI

logging.basicConfig()


class GameMatch:
    game = None
    ws1 = None
    ws2 = None
    stored_deck = None
    vs_ai = False
    lock = None

    def __init__(self, ws):
        self.ws1 = ws

        self.lock = asyncio.Lock()

    # Notify each player how many players are connected
    async def notify_number_players_connected(self):
        ready = self.ws2 is not None or self.vs_ai
        message = json.dumps({"type": "both_players_connected", "value": ready})

        active_ws = []
        if self.ws1 is not None:
            active_ws.append(self.ws1)
        if self.ws2 is not None:
            active_ws.append(self.ws2)
        await asyncio.wait([ws.send(message) for ws in active_ws])

    # If game has started, notify each player the state of the game
    async def notify_state(self):
        if self.game is None:
            return

        messages = []
        if self.ws1 is not None:
            messages.append(self.ws1.send(self.state_event(0)))
        if self.ws2 is not None:
            messages.append(self.ws2.send(self.state_event(1)))

        await asyncio.wait(messages)

        # If vs an ai opponent, they may now have a chance to act
        if self.vs_ai and self.game.model.priority == 1:
            await self.opponent_acts()

    def state_event(self, player):
        return json.dumps({"type": "transmit_state", "value": self.game.get_client_model(player)})

    # TODO Tell player that their opponent has left - be aware there could only be 1 ws
    async def notify_exit(self):
        pass

    def add_player_2(self, ws):
        self.ws2 = ws

        return self

    async def do_mulligan(self, player, mulligan):
        async with self.lock:
            self.game.do_mulligan(player, mulligan)
            if self.vs_ai:
                self.game.do_mulligan(1, (False, False, False))

    # Do the given action, if it is valid inform others of changed state, otherwise signal error to player
    async def do_action(self, player, action, version):
        valid = None
        async with self.lock:
            valid = self.game.on_player_input(player, action, version)

        if valid:
            await self.notify_state()
        else:
            ws = self.ws1 if player == 0 else self.ws2
            await notify_error(ws)

    async def add_ai_opponent(self):
        await self.add_deck(1, get_computer_deck())
        self.vs_ai = True

    async def add_deck(self, player, deck):
        async with self.lock:
            if self.stored_deck is None:
                self.stored_deck = deck
            else:
                if player == 0:
                    self.game = ServerController(deck, self.stored_deck)
                else:
                    self.game = ServerController(self.stored_deck, deck)
                self.game.start()

    # Opponent plays cards until they don't have priority
    async def opponent_acts(self):
        async with self.lock:
            opponent_model = ClientModel(self.game.get_client_model(1))
            opponent_action = AI.get_action(opponent_model)

            valid = self.game.on_player_input(1, opponent_action)

        # If my opponent acted, notify state
        if valid:
            await self.notify_state()


class TutorialMatch(GameMatch):
    def __init__(self, ws):
        super().__init__(ws)

        self.vs_ai = True

        # Start a tutorial game
        self.game = TutorialController()
        self.game.start()

    async def add_deck(self, player, deck):
        return


# Notify the user that they have done something wrong (Played an impossible card, etc)
async def notify_error(ws):
    msg = json.dumps({"type": "signal_error"})
    await asyncio.wait([ws.send(msg)])

# A dictionary with paths (passwords) as keys
PWD_MATCHES = {}
matches_lock = asyncio.Lock()
async def serveMain(ws, path):
    global PWD_MATCHES

    # Remove leading /
    path = path[1:]

    if path == 'ai':
        player = 0
        match = GameMatch(ws)
        await match.add_ai_opponent()
    elif path == 'tutorial':
      player = 0
      match = TutorialMatch(ws)
    else:
        # This ensures that 2 players won't both think they're first or second
        async with matches_lock:
            if path not in PWD_MATCHES.keys():
                player = 0
                match = GameMatch(ws)
                PWD_MATCHES[path] = match
            else:
                player = 1
                match = PWD_MATCHES.pop(path).add_player_2(ws)

    await match.notify_number_players_connected()

    # Listen to the ws and respond accordingly
    try:
        async for message in ws:
            print(message)
            data = json.loads(message)
            print(data)

            if data["type"] == "init":
                deck = CardCodec.decode_deck(data["value"])
                print(deck)

                await match.add_deck(player, deck)

                await match.notify_state()

            elif data["type"] == "mulligan":
                mulligan = CardCodec.decode_mulligans(data["value"])
                await match.do_mulligan(player, mulligan)

                await match.notify_state()

            elif data["type"] == "play_card":
                await match.do_action(player, data["value"], data["version"])

            elif data["type"] == "pass_turn":
                # TODO 10 is the pass action, use the constant for pass to avoid arbitrary literal
                await match.do_action(player, 10, data["version"])

    finally:
        # If this player was searching for an opponent and left, remove their open match
        async with matches_lock:
            if path in PWD_MATCHES:
                print("My opponent left before we got into a game. " + path)
                PWD_MATCHES.pop(path)

        await match.notify_exit()


# ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
# # print(os.getcwd())
# # localhost_pem = open("cert.pem")
# localhost_pem = pathlib.Path(__file__).parents[0].with_name("cert.pem")
# ssl_context.load_cert_chain(localhost_pem)


def main():
    start_server = websockets.serve(serveMain, LOCAL, PORT)#, ping_interval=None, ssl=foo)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

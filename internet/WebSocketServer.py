import asyncio
import json
import logging
import websockets
import ssl

from internet.Settings import *
import CardCodec
from logic.ServerController import ServerController

logging.basicConfig()


class GameMatch:
    game = None
    ws1 = None
    ws2 = None
    stored_deck = None

    def __init__(self, ws):
        self.ws1 = ws

    # Notify each player how many players are connected
    async def notify_number_players_connected(self):
        message = json.dumps({"type": "both_players_connected", "value": (self.ws2 is not None)})

        active_ws = [self.ws1, self.ws2] if self.ws2 else [self.ws1]
        await asyncio.wait([ws.send(message) for ws in active_ws])

    # If game has started, notify each player the state of the game
    async def notify_state(self):
        if self.game is None:
            return

        wss = [self.ws1, self.ws2]
        await asyncio.wait([wss[i].send(self.state_event(i)) for i in [0, 1]])

    def state_event(self, player):
        return json.dumps({"type": "transmit_state", "value": self.game.get_client_model(player)})

    # TODO Tell player that their opponent has left - be aware there could only be 1 ws
    async def notify_exit(self):
        pass

    def add_player_2(self, ws):
        self.ws2 = ws

        return self

    def add_deck(self, player, deck):
        if self.stored_deck is None:
            self.stored_deck = deck
        else:
            if player == 0:
                self.game = ServerController(deck, self.stored_deck)
            else:
                self.game = ServerController(self.stored_deck, deck)
            self.game.start()


USERS = []
# Not passworded
MATCHES = []
# Passworded
PWD_MATCHES = {}


# Notify the user that they have done something wrong (Played an impossible card, etc)
async def notify_error(ws):
    msg = json.dumps({"type": "signal_error"})
    await asyncio.wait([ws.send(msg)])


# A match being formed which only has 1 player
NEXT_MATCH = None
async def serveMain(ws, path):
    global NEXT_MATCH

    if NEXT_MATCH is None:
        player = 0
        match = NEXT_MATCH = GameMatch(ws)

    else:
        player = 1
        match = NEXT_MATCH.add_player_2(ws)
        NEXT_MATCH = None

    await match.notify_number_players_connected()

    # Listen to the ws and respond accordingly
    try:
        async for message in ws:
            print(message)
            data = json.loads(message)

            if data["type"] == "init":
                deck = CardCodec.decode_deck(data["value"])
                print(deck)

                match.add_deck(player, deck)

                await match.notify_state()

            elif data["type"] == "mulligan":
                mulligan = CardCodec.decode_mulligans(data["value"])
                # TODO Move this into the GameMatch class instead of grabbing its attribute
                match.game.do_mulligan(player, mulligan)
                await match.notify_state()

            elif data["type"] == "play_card":
                # TODO Move this into the GameMatch class instead of grabbing its attribute
                if match.game.on_player_input(player, data["value"]):
                    await match.notify_state()
                else:
                    await notify_error(ws)

            elif data["type"] == "pass_turn":
                # TODO Move this into GameMatch class
                if match.game.on_player_input(player, 10):
                    await match.notify_state()
                else:
                    await notify_error(ws)

    finally:
        # If this player was searching for an opponent and left, remove that open match
        if match is NEXT_MATCH:
            print("My opponent left before we got into a game.")
            NEXT_MATCH = None

        await match.notify_exit()


ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

def main():
    start_server = websockets.serve(serveMain, LOCAL, PORT, ping_interval=None, ssl=ssl_context)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

import asyncio
import json
import logging
import websockets
import ssl
import pathlib
import os
import Authenticate
import re

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
    sotre_avatar = None
    vs_ai = False
    lock = None

    # UUIDs for the players to receive currency if they win
    uuid1 = None
    uuid2 = None

    def __init__(self, ws, uuid=None):
        self.ws1 = ws

        self.uuid1 = uuid

        self.lock = asyncio.Lock()

    def has_begun(self):
        return self.game is not None

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

        # Give the winner igc if they just won, then remove their uuid so they aren't double paid
        winner = self.game.model.get_winner()
        if winner == 0:
            if self.uuid1 is not None:
                Authenticate.add_win(self.uuid1)
                self.uuid1 = None
            if self.uuid2 is not None:
                Authenticate.add_loss(self.uuid2)
                self.uuid2 = None
        elif winner == 1:
            if self.uuid1 is not None:
                Authenticate.add_loss(self.uuid1)
                self.uuid1 = None
            if self.uuid2 is not None:
                Authenticate.add_win(self.uuid2)
                self.uuid2 = None

        messages = []
        if self.ws1 is not None:
            messages.append(self.ws1.send(self.state_event(0)))
        if self.ws2 is not None:
            messages.append(self.ws2.send(self.state_event(1)))

        await asyncio.wait(messages)

        # If vs an ai opponent, they may now have a chance to act
        if self.vs_ai and self.game.model.priority == 1 and False not in self.game.model.mulligans_complete:
            await self.opponent_acts()

    def state_event(self, player):
        return json.dumps({"type": "transmit_state", "value": self.game.get_client_model(player)})

    async def notify_exit(self, disconnecting_ws=None):
        # Don't inform after the game has ended, since users will naturally dc
        if self.game is None or self.game.model.get_winner() is not None:
            return

        # Remove the disconnecting ws
        if self.ws1 == disconnecting_ws:
            self.ws1 = None
        elif self.ws2 == disconnecting_ws:
            self.ws2 = None

        messages = []
        if self.ws1 is not None and not self.ws1.closed:
            messages.append(self.ws1.send(json.dumps({"type": "dc"})))
        if self.ws2 is not None and not self.ws2.closed:
            messages.append(self.ws2.send(json.dumps({"type": "dc"})))

        if messages:
            await asyncio.wait(messages)

    def add_player_2(self, ws, uuid=None):
        self.ws2 = ws

        self.uuid2 = uuid

        return self

    async def do_mulligan(self, player, mulligan):
        async with self.lock:
            self.game.do_mulligan(player, mulligan)

            # Mute one of the mulligans, to avoid both shuffle being audible at once
            if self.vs_ai:
                self.game.model.sound_effect = None

            # Issue because ai acts after this, notify_state is 2 things
            await self.notify_state()

            if self.vs_ai:
                self.game.do_mulligan(1, (False, False, False, False))

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

    async def add_ai_opponent(self, i=None):
        await self.add_deck(1, get_computer_deck(i), 0)
        self.vs_ai = True

    async def add_specific_ai_opponent(self, deck_code):
        await self.add_deck(1, CardCodec.decode_deck(deck_code), 0)
        self.vs_ai = True

    async def add_deck(self, player, deck, avatar):
        async with self.lock:
            if self.stored_deck is None:
                self.stored_deck = deck
                self.stored_avatar = avatar
            else:
                if player == 0:
                    self.game = ServerController(deck, self.stored_deck, avatar, self.stored_avatar)
                else:
                    self.game = ServerController(self.stored_deck, deck, self.stored_avatar, avatar)
                self.game.start()

                # Print out what's happening
                def deck_to_string(d):
                    s = ''
                    for card in d:
                        s += card.name + ', '
                    return s
                if player == 0:
                    d1 = deck_to_string(deck)
                    d2 = deck_to_string(self.stored_deck)
                else:
                    d1 = deck_to_string(self.stored_deck)
                    d2 = deck_to_string(deck)

                s = "Game started between ips:"
                if self.ws1 is not None:
                    s += f" {self.ws1.remote_address} "
                if self.ws2 is not None:
                    s += f" {self.ws2.remote_address} "
                s += f"\nDecks:\n{d1}\n{d2}\n"
                print(s)

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
    def __init__(self, ws, num=None):
        super().__init__(ws)

        self.vs_ai = True

        # Start a tutorial game
        self.game = TutorialController(num)
        self.game.start()
        self.game.do_mulligan(0, [False, False, False])
        self.game.do_mulligan(1, [False, False, False])
        self.game.model.version_no = 0

    async def add_deck(self, player, deck, avatar):
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

    if path == 'tokensignin':
        await Authenticate.authenticate(ws)
        return

        # Wait for player to seek a match
        # async for message in ws:
        #     data = json.loads(message)
        #
        #     match, player = await get_match(ws, '')
    else:
        match, player = await get_match(ws, path)

    # Listen to the ws and respond accordingly
    try:
        async for message in ws:
            data = json.loads(message)

            await handle_game_messages(data, match, player)

    finally:
        await match_cleanup(path, match)


# Do any cleanup that must happen after a match ends
async def match_cleanup(path, match, ws=None):
    # If this player was searching for an opponent and left, remove their open match
    async with matches_lock:
        # If the match hasn't begun
        if match is None or not match.has_begun():
            if path in PWD_MATCHES:
                print("Player left before getting into a game. " + path)
                PWD_MATCHES.pop(path)

    await match.notify_exit(ws)


# Get a match for this websocket / path pair
async def get_match(ws, path, uuid=None):
    if path == 'ai':
        player = 0
        match = GameMatch(ws, uuid)
        await match.add_ai_opponent()
    elif path.startswith('ai-'):
        player = 0
        match = GameMatch(ws, uuid)
        i = path[3:]
        await match.add_ai_opponent(i)
    # Tutorials in the adventure mode
    elif path.startswith('ai:t'):
        player = 0
        tutorial_number = int(path[4:])
        match = TutorialMatch(ws, tutorial_number)
    elif path.startswith('ai:'):
        player = 0
        match = GameMatch(ws, uuid)
        deck_code = path[3:]
        await match.add_specific_ai_opponent(deck_code)
    # TODO Remove
    elif path == 'tutorial':
      player = 0
      match = TutorialMatch(ws)
    else:
        # This ensures that 2 players won't both think they're first or second
        async with matches_lock:
            if path not in PWD_MATCHES.keys():
                player = 0
                match = GameMatch(ws, uuid)
                PWD_MATCHES[path] = match
            else:
                player = 1
                match = PWD_MATCHES.pop(path).add_player_2(ws, uuid)

    await match.notify_number_players_connected()

    return match, player

# Handle any messages related to the match occuring
async def handle_game_messages(data, match, player):
    if data["type"] == "init":
        deck = CardCodec.decode_deck(data["value"])
        avatar = data["avatar"]

        await match.add_deck(player, deck, avatar)

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
    # elif data["type"] == "exit_match":
    #     break
    else:
        print(data["type"])

# ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
# # print(os.getcwd())
# # localhost_pem = open("cert.pem")
# localhost_pem = pathlib.Path(__file__).parents[0].with_name("cert.pem")
# ssl_context.load_cert_chain(localhost_pem)


def main():
    start_server = websockets.serve(serveMain, LOCAL, PORT)#, ping_interval=None, ssl=foo)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

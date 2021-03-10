import asyncio
import json
import logging
import websockets
import ssl

from internet.Settings import *
import CardCodec
from logic.ServerController import ServerController

logging.basicConfig()

STATE = {"value": 0}

USERS = []

game = None


def state_event(player):
    return json.dumps({"type": "transmit_state", "value": game.get_client_model(player)})


def users_event():
    return json.dumps({"type": "both_players_connected", "value": len(USERS) == 2})


async def notify_state():
    if USERS:  # asyncio.wait doesn't accept an empty list
        await asyncio.wait([USERS[i].send(state_event(i)) for i in range(len(USERS))])


async def notify_users():
    print(f'Do we have user? {USERS}')
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = users_event()
        await asyncio.wait([user.send(message) for user in USERS])


async def register(websocket):
    USERS.append(websocket)
    print('about to notify')
    await notify_users()


async def unregister(websocket):
    USERS.remove(websocket)
    await notify_users()


deck1 = None
async def main(websocket, path):
    print(f'Main has start ws: {dir(websocket)}\n*: {websocket}')
    global game
    global deck1

    # Which player I am
    player = None

    # register(websocket) sends user_event() to websocket
    print('about to register')
    await register(websocket)
    try:
        async for message in websocket:
            print(message)
            data = json.loads(message)

            if data["type"] == "init":
                deck = CardCodec.decode_deck(data["value"])
                print(deck)

                if deck1 is None:
                    deck1 = deck
                    player = 0

                else:
                    player = 1

                    # TODO locks
                    game = ServerController(deck1, deck)
                    game.start()

                    # So that reconnects don't reuse the previous deck
                    deck1 = None

                    await notify_state()
            elif data["type"] == "mulligan":
                mulligan = CardCodec.decode_mulligans(data["value"])
                game.do_mulligan(player, mulligan)
                await notify_state()

            elif data["type"] == "play_card":
                if game.on_player_input(player, data["value"]):
                    await notify_state()

            elif data["type"] == "pass_turn":
                if game.on_player_input(player, 10):
                    await notify_state()

    finally:
        await unregister(websocket)


# ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

def main():
    start_server = websockets.serve(main, LOCAL, PORT, ping_interval=None)#, ssl=ssl_context)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

import socketserver
import threading
import json
import time

import CardCodec
from logic.ServerController import ServerController
from internet.Settings import *

# Number of threads of the handler, used to assign player number to each
thread_counter = 0
deck1 = None
# Model should be started once both decks are received
game = None
class ThreadedTCPRequestHandler(socketserver.StreamRequestHandler):
    """
    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        global thread_counter
        global deck1
        global game

        player = thread_counter
        thread_counter += 1

        try:
            deck_received = False
            while not deck_received:
                # The first message received is in bytes because it contains the player's deck
                msg = self.rfile.readline().strip().decode()

                if msg.startswith(INIT_MSG):
                    deck = CardCodec.decode_deck(msg.split(':', 1)[1])

                    # If this is the first player, set this as deck1 and wait for the 2nd deck to arrive
                    if not deck1:
                        deck1 = deck

                        # Wait for the 2nd deck to be received
                        while not game:
                            time.sleep(1)

                    else:
                        game = ServerController(deck1, deck)
                        game.start()

                    self.request.send("fooo boo whoo".encode())

                    deck_received = True

            while True:
                # TODO fix
                msg = self.rfile.readline().strip().decode()

                if msg.startswith(GET_STATE):
                    client_version_num = int(msg.split(':', 1)[1])

                    if client_version_num is game.model.version_no:
                        self.request.send(NO_UPDATE.encode())

                    else:
                        serialized_model = json.dumps(game.get_client_model(player))
                        response = f"{UPDATE}:{serialized_model}".encode()
                        self.wfile.write(response)

                elif msg.startswith(DO_ACTION):
                    action = int(msg.split(':', 1)[1])

                    # Whether the choice was valid
                    valid = game.on_player_input(player, action)

                    # TODO care about if valid
                    if valid:
                        self.wfile.write(VALID_CHOICE.encode())
                    else:
                        self.wfile.write(INVALID_CHOICE.encode())
                else:
                    self.wfile.write(INVALID_CHOICE.encode())
        except ConnectionResetError as e:
            print(e)
            self.finish()

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def main():
    server = ThreadedTCPServer((LOCAL, PORT), ThreadedTCPRequestHandler)

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever(poll_interval=1))

    # Exit the server thread when the main thread terminates
    # server_thread.daemon = True
    server_thread.start()
    print("Server loop running in thread:", server_thread.name)

        # server.shutdown()


if __name__ == '__main__':
    main()

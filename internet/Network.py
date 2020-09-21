# This borrows extensively from Tech With Tim's tutorial on Python Networking:
# https://github.com/techwithtim/Network-Game-Tutorial

import socket
import json

import CardCodec
from internet.Settings import *
from logic.ClientModel import ClientModel

class Network:
    def __init__(self, deck):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((HOST, PORT))

        # Send that starting deck
        deck_codes = CardCodec.encode_deck(deck)
        msg = f"{INIT_MSG}:{deck_codes}\n"

        try:
            self.conn.send(msg.encode())
            response = self.conn.recv(BUFSIZE).decode()
        except:
            print("Problem sending the starting deck")

        # NOTE Here, I could make 2 threads with this socket an argument to both
        # One would send actions
        # The other would listen for state

    def on_tic(self, model, action):
        response = self.get_state(model)

        if response is None:
            self.send_action(action)
            return None
        else:
            # Our version of state is outdated, don't take the action, do return the stated we got back
            return response

    # Ask the server for state
    # Include the version num of the state we have
    # So that if nothing has changed, we don't update
    def get_state(self, model):
        if model is None:
            version_num = -1
        else:
            version_num = model.version_num

        msg = f"{GET_STATE}:{version_num}\n".encode()

        self.conn.send(msg)
        response = self.conn.recv(BUFSIZE)

        if response.startswith(NO_UPDATE.encode()):
            return None
        else:
            # The response is the new state, decode and return it
            encoded_state = response.split(b':', 1)[1]
            return ClientModel(json.loads(encoded_state))

    # Send the server an action that the user wishes to take
    def send_action(self, action):
        if action is not None:
            msg = f"{DO_ACTION}:{action}\n"

            try:
                self.conn.send(msg.encode())
                response = self.conn.recv(BUFSIZE).decode()

                # TODO care about returned responses
                return response

            except:
                print("problem")

                # TODO Experimental, if it failed, try again
                return self.send_action(action)

import os
import asyncio
import psycopg2
import json

import psycopg2.sql
import internet.WebSocketServer as game_server
import websockets

from bottle import run, post, request, response, get, route
from google.oauth2 import id_token
from google.auth.transport import requests

from internet.Settings import *
# from logic.Pack import get_random_pack


# The id for the google_api for oauth2
CLIENT_ID = '574352055172-n1nqdc2nvu3172levk2kl5jf7pbkp4ig.apps.googleusercontent.com'
COST_PACK = 100
IGC_INDEX = 1
WIN_AMT = 15

# Just take the app part of the url
if platform.system() == 'Darwin':
    HOST = 'Local build does not use authenticate'
else:
    HOST = os.environ["DATABASE_URL"].split('@')[1].split(':')[0]


# NOTE Have to add 1 for working with sql arrays, they start at 1

# Make a list of uuids and if they are signed in
signed_in_uuids = {}

async def authenticate(ws):
    # Send a request for token
    message = json.dumps({"type": "request_token"})
    await asyncio.wait([ws.send(message)])

    # Data about this user, stored locally for session
    user_data = None
    # The last set of choice cards user saw, should always be set before choice is made
    choice_cards = [0, 0, 0]

    path = None
    uuid = None

    # Listen to responses
    try:
        async for message in ws:
            data = json.loads(message)

            if data["type"] == "send_token":
                # token = data['token']
                # (uuid, email) = get_id_email(token)

                # TODO User a token that can be authenticated instead of trusting the uuid and email
                uuid = data['uuid']
                num_digits = len(str(uuid))
                uuid = str(uuid) + '0' * (32 - num_digits)

                email = data['email']

                # If no uuid was returned, this token is invalid
                if uuid is None:
                    message = json.dumps({"type": "invalid_token"}, default=str)
                    await asyncio.wait([ws.send(message)])
                    await ws.close()
                    continue

                elif uuid in signed_in_uuids:
                    # If signed in ws is still open, alert user of error
                    try:
                        await signed_in_uuids[uuid].ensure_open()

                        # Set to None to not pop this uuid from signed in uuids below!
                        uuid = None
                        message = json.dumps({"type": "already_signed_in"}, default=str)
                        await asyncio.wait([ws.send(message)])
                        await ws.close()
                        continue

                    # If existing connection is closed, sign in this user as normal below
                    except websockets.ConnectionClosed as e:
                        pass

                signed_in_uuids[uuid] = ws
                user_data = get_user_data(uuid, email)

                # If user's account is just being created, prompt them to init it
                if user_data is None:
                    message = json.dumps({"type": "prompt_user_init"}, default=str)
                else:
                    message = json.dumps({"type": "send_user_data", "value": user_data}, default=str)

                await asyncio.wait([ws.send(message)])
            # TODO Ensure that this ws is the signed in one in the above hashmap before doing any of the following operations
            elif data["type"] == "send_user_progress":
                adjust_user_progress(uuid, data["value"])
            elif data["type"] == "send_decks":
                adjust_decks(uuid, data["value"])
            elif data["type"] == "send_inventory":
                adjust_inventory(uuid, data["value"])
            elif data["type"] == "send_completed_missions":
                adjust_completed_missions(uuid, data["value"])
            elif data["type"] == "find_match":
                path = data["value"]
                print("User with email: " + email + " Is looking for a match with value: " + path)

                match, player = await game_server.get_match(ws, path, uuid)
            elif data["type"] == "exit_match":
                # print('Exiting match for signed in user with uuid: ' + uuid)
                await game_server.match_cleanup(path, match, ws)
                path = match = None
            # In all other cases the message has to do with a game action, so it should be handled as a game message
            else:
                await game_server.handle_game_messages(data, match, player)
    except websockets.exceptions.ConnectionClosedError as e:
        print("Connection closed error:")
        print(e.reason)
        print(e.code)
    finally:
        # Exit from any games that user was in / matchmaking that user was in
        if path is not None:
            await game_server.match_cleanup(path, match)

        if uuid is not None:
            # Remove this account from list of signed in accounts
            signed_in_uuids.pop(uuid)

# Accept POSTs from gapi, keep a log of the jti's
jtis = {}
@post('/gapi')
def handle_gapi():
    token = request.body.read()
    print(token)

    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        userid = idinfo['sub']
        email = idinfo['email']
        jti = idinfo['jti']
        print(email)
        jtis[jti] = True
    except ValueError:
        # Invalid token
        pass
    #
    # csrf_token_cookie = request.cookies.get('g_csrf_token')
    # if not csrf_token_cookie:
    #     webapp2.abort(400, 'No CSRF token in Cookie.')
    # csrf_token_body = self.request.get('g_csrf_token')
    # if not csrf_token_body:
    #     webapp2.abort(400, 'No CSRF token in post body.')
    # if csrf_token_cookie != csrf_token_body:
    #     webapp2.abort(400, 'Failed to verify double submit cookie.')
# TODO
# run(host='celestialtcg.com/gapi')

def get_id_email(token):
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

        # Postgres uuid requires 32 (hex) digits, so add trailing 0s to get that many digits
        id = idinfo['sub']
        num_digits = len(str(id))
        padded_id = str(id) + '0' * (32 - num_digits)

        return padded_id, idinfo['email']

    except ValueError:
        return (None, None)

# Interact with the psql
# Get the user data for the given user id, create it first if they don't yet have an account
# Returns a tuple if there is data, None otherwise
def get_user_data(id, email):
    try:
        # Connect to an existing database
        connection = psycopg2.connect(user="postgres",
                                      password=os.environ["DB_PWD"],
                                      host=HOST,
                                      port="5432",
                                      database="celestial",
                                      sslmode="disable")

        cursor = connection.cursor()

        # Check if user has an entry
        cursor.execute(
            "SELECT * FROM players WHERE id = '%(id)s'",
            {'id': id})
        count = cursor.rowcount
        # TODO Throw if there is more than one row with that uuid
        if count > 0:
            # If they do, return that entry
            user_data = cursor.fetchone()
            # print(f"Requested user data is: {user_data}")
            return user_data

        else:
            # TODO Take the user's preexisting progress / decks here

            # If they don't create one, then return the basic entry
            cursor.execute(
                "INSERT INTO players (ID, EMAIL) VALUES ('%(id)s', '%(email)s')",
                {'id': id, 'email': email})
            connection.commit()

            print(f"Created the basic entry for user: {email}")
            return None

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            # print("PostgreSQL connection is closed")

# For user with given id, update their user progress
def adjust_user_progress(uuid, user_progress):
    # SQL db uses curly brace instead of square for arrays
    progress_no_quotes = str(user_progress).replace("'", "").replace('[', '{').replace(']', '}')

    update_db(
        """
        UPDATE players
        SET userprogress = %(progress_no_quotes)s
        WHERE id = %(uuid)s;
        """,
        {'progress_no_quotes': progress_no_quotes, 'uuid': uuid}
    )

# For user with given id, update their decks
def adjust_decks(uuid, decks):
    # SQL db uses curly brace instead of square for arrays
    decks_no_quotes = str(decks).replace("'", "").replace('[', '{').replace(']', '}')

    update_db(
        """
        UPDATE players
        SET decks = %(decks_no_quotes)s
        WHERE id = %(uuid)s;
        """,
        {'decks_no_quotes': decks_no_quotes, 'uuid': uuid}
    )

# For user with given id, update their inventory
def adjust_inventory(uuid, binary_string):
    update_db(
        """
        UPDATE players
        SET inventory = %(binary_string)s
        WHERE id = %(uuid)s;
        """,
        {'binary_string': binary_string, 'uuid': uuid}
    )

# For user with given id, update their completed missions
def adjust_completed_missions(uuid, binary_string):
    update_db(
        """
        UPDATE players
        SET completedmissions = %(binary_string)s
        WHERE id = %(uuid)s;
        """,
        {'binary_string': binary_string, 'uuid': uuid}
    )

# For user with given id, add them a win's worth of igc and record 1 win
def add_win(uuid):
    update_db(
        """
        UPDATE players
        SET wins = wins + 1
        WHERE id = %(uuid)s;
        """,
        {'uuid': uuid}
    )

# For user with given id, record a loss
def add_loss(uuid):
    update_db(
        """
        UPDATE players
        SET losses = losses + 1
        WHERE id = %(uuid)s;
        """,
        {'uuid': uuid}
    )

# For user with given id, update their decks
def update_db(cmd, vars):
    # print(cmd)
    try:
        # Connect to an existing database
        connection = psycopg2.connect(user="postgres",
                                      password=os.environ["DB_PWD"],
                                      host=HOST,
                                      port="5432",
                                      database="celestial",
                                      sslmode="disable")

        cursor = connection.cursor()

        cursor.execute(cmd, vars)
        connection.commit()

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error, cmd, vars)
    finally:
        if connection:
            cursor.close()
            connection.close()
            # print("PostgreSQL connection is closed")

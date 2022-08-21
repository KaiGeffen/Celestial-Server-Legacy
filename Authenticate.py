import os
import asyncio
import psycopg2
import json
import internet.WebSocketServer as game_server

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

# NOTE Have to add 1 for working with sql arrays, they start at 1

async def authenticate(ws):
    # Send a request for token
    message = json.dumps({"type": "request_token"})
    await asyncio.wait([ws.send(message)])

    # Data about this user, stored locally for session
    user_data = None
    # The last set of choice cards user saw, should always be set before choice is made
    choice_cards = [0, 0, 0]

    # Listen to responses
    try:
        async for message in ws:
            data = json.loads(message)

            if data["type"] == "send_token":
                token = data['value']
                (uuid, email) = get_id_email(token)

                if email is None:
                    user_data = None
                else:
                    user_data = get_user_data(uuid, email)

                message = json.dumps({"type": "send_user_data", "value": user_data}, default=str)
                await asyncio.wait([ws.send(message)])
            elif data["type"] == "request_pack":
                print('User tried to buy a pack but that feature is deprecated.')
                return
                #
                # # Check if they have the funds
                # have_funds = user_data[IGC_INDEX] >= COST_PACK
                #
                # # If not, return error
                # if not have_funds:
                #     message = json.dumps({"type": "error"})
                # else:
                #     pack = get_random_pack()
                #
                #     # Subtract funds, add these cards to user inventory
                #     # The first card of the choosables is picked by default,
                #     # then if another is chosen, the inventory is adjusted
                #     adjust_user_data_opened_pack(uuid, pack)
                #
                #     # choice_cards = pack[4:]
                #     choice_cards[0] = pack[4]
                #     choice_cards[1] = pack[5]
                #     choice_cards[2] = pack[6]
                #
                #     message = json.dumps({"type": "send_pack", "value": pack})
                # await asyncio.wait([ws.send(message)])
            elif data["type"] == "make_choice":
                print('User tried to choose a card from a pack but that feature is deprecated.')
                return
                #
                # chosen_card = choice_cards[data['value']]
                #
                # # Adjust the inventory to reflect if user chose a card besides the first option
                # adjust_user_data_chosen_card(uuid, chosen_card, choice_cards[0])
                #
                # # Get the user's data
                # if email is None:
                #     user_data = None
                # else:
                #     user_data = get_user_data(uuid, email)
                #
                # message = json.dumps({"type": "send_user_data", "value": user_data}, default=str)
                # await asyncio.wait([ws.send(message)])
            elif data["type"] == "send_user_progress":
                adjust_user_progress(uuid, data["value"])
            elif data["type"] == "send_decks":
                adjust_decks(uuid, data["value"])
            elif data["type"] == "find_match":
                path = data["value"]

                match, player = await game_server.get_match(ws, path, uuid)
            elif data["type"] == "exit_match":
                await game_server.match_cleanup(path, match)
                path = match = None
            # In all other cases the message has to do with a game action, so it should be handled as a game message
            else:
                await game_server.handle_game_messages(data, match, player)
    finally:
        # Exit from any games that user was in / matchmaking that user was in
        if path is not None:
            await game_server.match_cleanup(path, match)


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
        connection = psycopg2.connect(user="doadmin",
                                      password=os.environ["DB_PWD"],
                                      host=os.environ["DATABASE_URL"],
                                      #"app-8058d91d-8288-43bb-a12e-e1eb61ce00e3-do-user-8861671-0.b.db.ondigitalocean.com",
                                      port="25060",
                                      database="db",
                                      sslmode="require")

        cursor = connection.cursor()

        # Check if user has an entry
        select_query = f"SELECT * from players where id = '{id}'"
        cursor.execute(select_query)
        count = cursor.rowcount
        if count > 0:
            # If they do, return that entry
            user_data = cursor.fetchone()
            print(f"Request user data is: {user_data}")
            return user_data

        else:
            # If they don't create one, then return the basic entry
            print("User doesn't yet exist")

            basic_entry = f"('{id}', '{email}')"
            insert_query = f"INSERT INTO players (ID, EMAIL) VALUES {basic_entry}"
            cursor.execute(insert_query)
            connection.commit()

            # Fetch this user's fresh data
            cursor.execute(select_query)
            user_data = cursor.fetchone()

            print(f"Created the basic entry: {user_data}")
            return user_data

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

# For user with given id, add the given pack to their inventory
def adjust_user_data_opened_pack(uuid, pack):
    update_query = "UPDATE players\n"
    update_query += f"SET igc = igc - {COST_PACK}" \

    for i in range(5):
        val = pack[i]

        # Must increase by amt of the card in the first 5 because it won't get saved between successive increments
        amt = pack[:5].count(val)

        update_query += f", inventory[{val + 1}] = coalesce(inventory[{val + 1}], 0) + {amt}"
    update_query += f"\nWHERE id = '{uuid}';"

    update_db(update_query)

# For user with given id, submit their choice (Remove the default chosen card, add the one they chose)
def adjust_user_data_chosen_card(uuid, chosen_card, default_card):
    if chosen_card == default_card:
        return

    try:
        # Connect to an existing database
        connection = psycopg2.connect(user="doadmin",
                                      password=os.environ["DB_PWD"],
                                      host="app-8058d91d-8288-43bb-a12e-e1eb61ce00e3-do-user-8861671-0.b.db.ondigitalocean.com",
                                      port="25060",
                                      database="defaultdb",
                                      sslmode="require")

        cursor = connection.cursor()

        update_query = "UPDATE players\n"
        update_query += f"SET inventory[{chosen_card + 1}] = coalesce(inventory[{chosen_card + 1}], 0) + 1, inventory[{default_card + 1}] = coalesce(inventory[{default_card + 1}], 0) - 1\n"
        update_query += f"WHERE id = '{uuid}';"

        cursor.execute(update_query)
        connection.commit()

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

# For user with given id, update their user progress
def adjust_user_progress(uuid, user_progress):
    # SQL db uses curly brace instead of square for arrays
    progress_no_quotes = str(user_progress).replace("'", "").replace('[', '{').replace(']', '}')

    update_query = "UPDATE players\n"
    update_query += f"SET userprogress = '{progress_no_quotes}'\n"
    update_query += f"WHERE id = '{uuid}';"

    update_db(update_query)

# For user with given id, update their decks
def adjust_decks(uuid, decks):
    decks_no_quotes = str(decks).replace("'", "").replace('[', '{').replace(']', '}')

    update_query = "UPDATE players\n"
    # SQL db uses curly brace instead of square for arrays
    update_query += f"SET decks = '{decks_no_quotes}'\n"
    update_query += f"WHERE id = '{uuid}';"

    update_db(update_query)

# For user with given id, add them a win's worth of igc and record 1 win
def add_win(uuid):
    update_query = "UPDATE players\n"
    update_query += f"SET igc = igc + {WIN_AMT}, wins = wins + 1"
    update_query += f"\nWHERE id = '{uuid}';"

    update_db(update_query)

# For user with given id, record a loss
def add_loss(uuid):
    update_query = "UPDATE players\n"
    update_query += f"SET losses = losses + 1"
    update_query += f"\nWHERE id = '{uuid}';"

    update_db(update_query)

# For user with given id, update their decks
def update_db(cmd):
    print(cmd)
    try:
        # Connect to an existing database
        connection = psycopg2.connect(user="doadmin",
                                      password=os.environ["DB_PWD"],
                                      host="app-8058d91d-8288-43bb-a12e-e1eb61ce00e3-do-user-8861671-0.b.db.ondigitalocean.com",
                                      port="25060",
                                      database="defaultdb",
                                      sslmode="require")

        cursor = connection.cursor()

        cursor.execute(cmd)
        connection.commit()

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

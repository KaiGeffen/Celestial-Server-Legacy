import os
import asyncio
import psycopg2
import json

from bottle import run, post, request, response, get, route
from google.oauth2 import id_token
from google.auth.transport import requests

from internet.Settings import *
from logic.Pack import get_random_pack


# The id for the google_api for oauth2
CLIENT_ID = '574352055172-n1nqdc2nvu3172levk2kl5jf7pbkp4ig.apps.googleusercontent.com'
COST_PACK = 100
IGC_INDEX = 2

async def authenticate(ws):
    # Send a request for token
    message = json.dumps({"type": "request_token"})
    print(message)
    await asyncio.wait([ws.send(message)])

    # Listen to responses
    async for message in ws:
        data = json.loads(message)

        # Data about this user, stored locally for session
        user_data = None
        # The last pack this user opened
        pack = None

        if data["type"] == "send_token":
            token = data['value']
            (uuid, email) = get_id_email(token)

            if uuid is None:
                user_data = None
            else:
                user_data = get_user_data(uuid, email)

            message = json.dumps({"type": "send_user_data", "value": user_data})
            print(message)
            await asyncio.wait([ws.send(message)])
        elif data["type"] == "open_pack":
            # Check if they have the funds
            have_funds = user_data[IGC_INDEX] >= COST_PACK

            # If not, return error
            if not have_funds:
                message = json.dumps({"type": "error"})
            else:
                pack = get_random_pack()

                # Subtract funds, add these cards to user inventory
                adjust_user_data_opened_pack(id, pack)

                message = json.dumps({"type": "pack", "value": pack})
            await asyncio.wait([ws.send(message)])
        elif data["type"] == "make_choice":
            # Adjust the inventory to reflect if user chose a card besides the first option
            pass




def get_id_email(token):
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
        print(idinfo['email'])
        return (idinfo['sub'], idinfo['email'])

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
                                      host="app-8058d91d-8288-43bb-a12e-e1eb61ce00e3-do-user-8861671-0.b.db.ondigitalocean.com",
                                      port="25060",
                                      database="defaultdb",
                                      sslmode="require")

        cursor = connection.cursor()

        # Check if user has an entry
        # Postgres uuid requires 32 (hex) digits, so add trailing 0s to get that many digits
        num_digits = len(str(id))
        padded_id = str(id) + '0' * (32 - num_digits)
        print(padded_id)
        select_query = f"SELECT * from players where id = '{padded_id}'"
        cursor.execute(select_query)
        count = cursor.rowcount
        if count > 0:
            # If they do, return that entry
            print("User exists")

            user_data = cursor.fetchone()
            print(f"Their data is: {user_data}")
            return user_data

        else:
            # If they don't create one, then return the basic entry
            print("User doesn't yet exist")

            basic_entry = f"('{padded_id}', '{email}', 0, '{{}}', 0, 0)"
            insert_query = f"INSERT INTO players (ID, EMAIL, IGC, DECKS, WINS, LOSSES) VALUES {basic_entry}"
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

import os
import psycopg2

from bottle import run, post, request, response, get, route
from google.oauth2 import id_token
from google.auth.transport import requests

from internet.Settings import *


# The id for the google_api for oauth2
CLIENT_ID = '574352055172-n1nqdc2nvu3172levk2kl5jf7pbkp4ig.apps.googleusercontent.com'

@route('/tokensignin', method = 'POST')
def process():
    print('Well Im in process')
    token = request.query['idtoken']
    return token + 'hewwo uwu'
    # Verify the given id, might be None
    userid = get_id(token)
    if userid is None:
        return 'That id is FAKE'
    return get_user_data(userid)

def get_id(token):
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
        return idinfo['sub']

    except ValueError:
        return None


def run_auth_server():
    run(host='0.0.0.0', port=PORT, debug=True)

run_auth_server()
print('Ran main')

id = '40e6215d-b5c6-4896-987c-f30f3678f608'
# Interact with the psql
# Get the user data for the given user id, create it first if they don't yet have an account
def get_user_data(id):
    try:
        # Connect to an existing database
        connection = psycopg2.connect(user="doadmin",
                                      password=os.environ("DB_PWD"),
                                      host="app-8058d91d-8288-43bb-a12e-e1eb61ce00e3-do-user-8861671-0.b.db.ondigitalocean.com",
                                      port="25060",
                                      database="defaultdb",
                                      sslmode="require")

        cursor = connection.cursor()

        # Check if user has an entry
        select_query = f"SELECT * from players where id = '{id}'"
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

            basic_entry = f"('{id}', 0, '{{}}', 0, 0)"
            insert_query = f"""INSERT INTO players (ID, IGC, DECKS, WINS, LOSSES) VALUES {basic_entry}"""
            cursor.execute(insert_query)
            connection.commit()

            print("Created the basic entry: " + basic_entry)
            return basic_entry

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

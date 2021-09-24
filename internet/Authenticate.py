from bottle import run, post, request, response, get, route

@route('/<id>',method = 'POST')
def process(id):
    # GET from server the entry at id

    # If none exists, POST the basic user data
    # Then return that basic data to the client

    # Otherwise, forward that data to the client
    return id


def run_auth_server():
    run(host='localhost', port=8080, debug=True)

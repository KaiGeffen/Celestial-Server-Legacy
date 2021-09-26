import internet.WebSocketServer as ws

# Runs the authentication server
# import threading
# import internet.Authenticate as auth

# print('Starting the authentication server...')
# threading.Thread(target=auth.run_auth_server).start()

print('Starting the websocket server...')
ws.main()

# Resources shared by both the Network and Server files

BUFSIZE = 4096 * 2
PORT = 5555
# The ipv4 address of the host machine. Run ipconfig from cmd to get this
HOST = "127.0.0.1"
LOCAL = "127.0.0.1"

# Time client waits between sending requests for changed state
CLIENT_WAIT = 0.01

# Messages
GET_STATE = 'Get'
DO_ACTION = 'Do'
INIT_MSG = 'Init'

# Responses
NO_UPDATE = 'No update'
UPDATE = 'Update'
INVALID_CHOICE = 'Invalid choice'

# Log into router, port forwarding, port 5555 to my local machine
# Tell my router goes to the ip I had been using
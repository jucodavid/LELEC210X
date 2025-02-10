import zmq
import numpy as np

PREAMB_LENGTH = 4
SYNC_LENGTH = 4

MELVEC_LENGTH = 20
N_MELVECS = 20

TAG_LENGTH = 16

def iint(x):
        return int(x, 16)
iint = np.vectorize(iint)

# Create a ZMQ context
context = zmq.Context()

# Create a SUB socket
socket = context.socket(zmq.SUB)

# Connect to the ZMQ PUB socket
socket.connect("tcp://127.0.0.1:10000")  # Replace with your PUB socket address

# Subscribe to all messages
socket.setsockopt_string(zmq.SUBSCRIBE, '')

while True:
    # Receive a message
    message = iint(socket.recv()[(PREAMB_LENGTH+SYNC_LENGTH):-(TAG_LENGTH)].hex(' ',2).split(' ')).reshape(N_MELVECS, MELVEC_LENGTH)
    print(message)

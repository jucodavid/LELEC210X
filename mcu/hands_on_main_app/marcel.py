import argparse

import zmq
from collections.abc import Iterator

import matplotlib.pyplot as plt
import numpy as np
from classification.utils.plots import plot_specgram
import pickle
import time

import requests
import json


ZMQ_ADDRESS = "tcp://127.0.0.1:10000"

PREAMB_LENGTH = 4
SYNC_LENGTH = 4
MELVEC_LENGTH = 12
N_MELVECS = 20
TAG_LENGTH = 16


# HOST_ADRESS = "http://localhost:5000"
# HOST_ADRESS = "http://lelec210x.sipr.ucl.ac.be"
# TEAM_KEY = "X6wLG0KYZwh0Op0BIiq0GdmEy4x7Ot3BDlRyecx-"
# TEAM_KEY = "a5vIbTLb5gDwxC2VXEj2lLuv4UAGSPmKm-iyCJVQ"


def iint(x):
        return int(x, 16)
iint = np.vectorize(iint)


def packet_parse(x):
    return iint(x[(PREAMB_LENGTH+SYNC_LENGTH):-(TAG_LENGTH)].hex(' ',2).split(' ')) #.reshape(N_MELVECS, MELVEC_LENGTH)


def reader() -> Iterator[str]:
    context = zmq.Context()
    socket = context.socket(zmq.SUB)

    socket.setsockopt(zmq.SUBSCRIBE, b"")
    socket.setsockopt(zmq.CONFLATE, 1)  # last msg only.

    socket.connect(ZMQ_ADDRESS)

    print(f"Reading packets from TCP address: {ZMQ_ADDRESS}")

    while True:
        msg = socket.recv()
        yield msg


def submit(guess):
    response = requests.post(f"{HOST_ADRESS}/lelec210x/leaderboard/submit/{TEAM_KEY}/{guess}", timeout=1)
    response_as_dict = json.loads(response.text)
    return (f"Response: {response_as_dict}")


if __name__ == "__main__":

    argParser = argparse.ArgumentParser()
    argParser.add_argument("-s", "--server", help="Server selection for submitting answers. LOCAL -> localhost:5000 UCL -> lelec210x.sipr.ucl.ac.be")
    argParser.add_argument("-t", "--time", help="Reset time.")
    argParser.add_argument("-m", "--memory", action='store_true', help="Use of memory for classification")
    argParser.add_argument("-ml", "--memory_length", help="Number of takes used for memory")
    argParser.add_argument("-p", "--plot", action='store_true', help="Plot Melvec")

    args = argParser.parse_args()

    if args.server is None:
        print("No server specified")
        print("fallback to localhost:5000 server")
        HOST_ADRESS = "http://localhost:5000"
        TEAM_KEY = "X6wLG0KYZwh0Op0BIiq0GdmEy4x7Ot3BDlRyecx-"
    elif args.server == "LOCAL":
        HOST_ADRESS = "http://localhost:5000"
        TEAM_KEY = "X6wLG0KYZwh0Op0BIiq0GdmEy4x7Ot3BDlRyecx-"
    elif args.server == "UCL":
        HOST_ADRESS = "http://lelec210x.sipr.ucl.ac.be"
        TEAM_KEY = "a5vIbTLb5gDwxC2VXEj2lLuv4UAGSPmKm-iyCJVQ"

    if args.time is not None:
        callout_time = float(args.time)
    else:
        callout_time = 3

    if args.memory is not None:
        memory = args.memory
    else:
        memory = False

    print("memory :", memory)

    if args.memory_length is not None:
        memory_length = int(args.memory_length)
    else:
        memory_length = 1

    print("length: ", memory_length)

    if args.plot is not None:
        plot_melvec = args.plot
    else:
        plot_melvec = False

    model_dir = "classification/data/models/"
    filename = "model_12.pickle"

    packet_counter = 0
    classnames = ['background','chainsaw','fire','fireworks','gunshot']
    predictions = np.zeros(len(classnames))
    model = pickle.load(open(model_dir + filename, "rb"))
    last = time.time()
    msg_counter = 0
    plt.figure(figsize=(4, 3))

    input_stream = reader()
    
    for packet in input_stream:
        waiting = time.time()
        if waiting - last > callout_time:
            packet_counter = 0
            predictions[:] = 0
            print("PREDICITONS RESET")
        last = time.time()

        msg_counter += 1
        melvec = packet_parse(packet)
        mat = np.zeros((2, len(melvec)))
        mat[0] = melvec / np.max(melvec)
        prediction = model.predict_proba(mat)[0]
        
        if packet_counter < memory_length - 1:
            predictions += prediction
            packet_counter += 1
        else:
            predictions += prediction
            packet_counter += 1
            predictions /= np.max([memory_length, packet_counter])
            # if (np.max(predictions) > np.mean(predictions) + 0.2):
            if True:
                a = classnames[np.argmax(predictions)]
                if a != 'background':
                    rep = submit(a)
                    print(f"{msg_counter}: {rep} ; prob {np.max(predictions):.3f}")
                else: 
                    print(f"{msg_counter}: Background guessed ; prob {np.max(predictions):.3f}")
                    rep = submit(classnames[2])
            else:
                print(f"{msg_counter}: Not enough confidence to submit ; prob {np.max(predictions):.3f}")

        if plot_melvec:
            plot_specgram(
                melvec.reshape((N_MELVECS, MELVEC_LENGTH)).T,
                ax=plt.gca(),
                is_mel=True,
                title=f"MEL Spectrogram #{msg_counter}",
                xlabel="Mel vector",
            )
            plt.tight_layout()
            plt.draw()
            plt.pause(.5)
            plt.clf()

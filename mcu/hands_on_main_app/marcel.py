import zmq
from collections.abc import Iterator

import matplotlib.pyplot as plt
import numpy as np
from classification.utils.plots import plot_specgram
import pickle


import requests
import json


ZMQ_ADDRESS = "tcp://127.0.0.1:10000"

PREAMB_LENGTH = 4
SYNC_LENGTH = 4
MELVEC_LENGTH = 20
N_MELVECS = 20
TAG_LENGTH = 16

# HOST_ADRESS = "http://localhost:5000"
HOST_ADRESS = "http://lelec210x.sipr.ucl.ac.be"
# TEAM_KEY = "X6wLG0KYZwh0Op0BIiq0GdmEy4x7Ot3BDlRyecx-"
TEAM_KEY = "a5vIbTLb5gDwxC2VXEj2lLuv4UAGSPmKm-iyCJVQ"


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
    print(f"Response: {response_as_dict}")


if __name__ == "__main__":
    model_dir = "classification/data/models/"
    filename = "model_rf_new.pickle"
    model = pickle.load(open(model_dir + filename, "rb"))

    msg_counter = 0
    plt.figure(figsize=(4, 3))

    input_stream = reader()
    for packet in input_stream:
        msg_counter += 1

        melvec = packet_parse(packet)
        # print(melvec)

        mat = np.zeros((2, len(melvec)))
        mat[0] = melvec / np.max(melvec)
        prediction = model.predict(mat)[0]

        submit(prediction)

        print(f"MEL Spectrogram #{msg_counter}")
        print(f"Class predicted: {prediction}")
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

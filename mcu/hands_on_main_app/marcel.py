import zmq
from collections.abc import Iterator

import matplotlib.pyplot as plt
import numpy as np

from classification.utils.plots import plot_specgram

import pickle
import sklearn.preprocessing as skpre
from classification.datasets import Dataset
from classification.utils.audio_student import AudioUtil, Feature_vector_DS
from classification.utils.utils import accuracy
from classification.utils.plots import show_confusion_matrix


ADDRESS = "tcp://127.0.0.1:10000"

PREAMB_LENGTH = 4
SYNC_LENGTH = 4

MELVEC_LENGTH = 20
N_MELVECS = 20

TAG_LENGTH = 16

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

    socket.connect(ADDRESS)

    print(f"Reading packets from TCP address: {ADDRESS}")

    while True:
        msg = socket.recv()
        yield msg

if __name__ == "__main__":
    model_dir = "../../classification/data/models/"
    filename = "model_rf_new.pickle"
    model = pickle.load(open(model_dir + filename, "rb"))

    msg_counter = 0
    plt.figure(figsize=(4, 3))

    input_stream = reader()
    for packet in input_stream:
        msg_counter += 1

        melvec = packet_parse(packet)
        print(melvec)

        mat = np.zeros((2, len(melvec)))
        mat[0] = melvec / np.max(melvec)
        prediction = model.predict(mat)
        print(prediction[0])


    #         print(f"MEL Spectrogram #{msg_counter}")
    #         print(f"Class predicted: {prediction[0]}")
    #         plot_specgram(
    #             melvec.reshape((N_MELVECS, MELVEC_LENGTH)).T,
    #             ax=plt.gca(),
    #             is_mel=True,
    #             title=f"MEL Spectrogram #{msg_counter}",
    #             xlabel="Mel vector",
    #         )
    #         plt.tight_layout()
    #         plt.draw()
    #         plt.pause(1)
    #         plt.clf()
    # except:
    #     print("caca")

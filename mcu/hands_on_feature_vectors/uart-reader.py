"""
uart-reader.py
ELEC PROJECT - 210x
"""

import argparse

import matplotlib.pyplot as plt
import numpy as np
import serial
from serial.tools import list_ports

from classification.utils.plots import plot_specgram

import pickle
import sklearn.preprocessing as skpre
from classification.datasets import Dataset
from classification.utils.audio_student import AudioUtil, Feature_vector_DS

PRINT_PREFIX = "DF:HEX:"
FREQ_SAMPLING = 10200
MELVEC_LENGTH = 20
N_MELVECS = 20

dt = np.dtype(np.uint16).newbyteorder("<")


def parse_buffer(line):
    line = line.strip()
    if line.startswith(PRINT_PREFIX):
        return bytes.fromhex(line[len(PRINT_PREFIX) :])
    else:
        print(line)
        return None


def reader(port=None):
    ser = serial.Serial(port=port, baudrate=115200)
    while True:
        line = ""
        while not line.endswith("\n"):
            line += ser.read_until(b"\n", size=2 * N_MELVECS * MELVEC_LENGTH).decode(
                "ascii"
            )
            print(line)
        line = line.strip()
        buffer = parse_buffer(line)
        if buffer is not None:
            buffer_array = np.frombuffer(buffer, dtype=dt)

            yield buffer_array


if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-p", "--port", help="Port for serial communication")
    args = argParser.parse_args()
    print("uart-reader launched...\n")

    if args.port is None:
        print(
            "No port specified, here is a list of serial communication port available"
        )
        print("================")
        port = list(list_ports.comports())
        for p in port:
            print(p.device)
        print("================")
        print("Launch this script with [-p PORT_REF] to access the communication port")

    else:
        input_stream = reader(port=args.port)
        msg_counter = 0

        model_dir = "../../classification/data/models/"
        filename = "model_rf_new.pickle"
        model = pickle.load(open(model_dir + filename, "rb"))
        plt.figure()
        for melvec in input_stream:
            msg_counter += 1
            mat = np.zeros((2, len(melvec)))
            mat[0] = melvec / np.linalg.norm(melvec)
            prediction = model.predict(mat)
            print("Class predicted :", prediction[0])

            proba = model.predict_proba(mat)
            print("Proba:\tbirds\tchainsaw\tfire\thandsaw\thelicopter")
            print(f"\t{proba[0,0]}\t{proba[0,1]}\t\t{proba[0,2]}\t{proba[0,3]}\t{proba[0,4]}\t")

            print(f"MEL Spectrogram #{msg_counter}")

            plot_specgram(
                melvec.reshape((N_MELVECS, MELVEC_LENGTH)).T,
                ax=plt.gca(),
                is_mel=True,
                title=f"MEL Spectrogram #{msg_counter}",
                xlabel="Mel vector",
            )
            plt.draw()
            plt.pause(1)
            plt.clf()


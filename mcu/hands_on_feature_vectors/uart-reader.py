"""
uart-reader.py
ELEC PROJECT - 210x
"""

import argparse

import matplotlib.pyplot as plt
import numpy as np
from numpy.dtypes import StringDType
import serial
from serial.tools import list_ports

from classification.utils.plots import plot_specgram

import pickle
import sklearn.preprocessing as skpre
from classification.datasets import Dataset
from classification.utils.audio_student import AudioUtil, Feature_vector_DS
from classification.utils.utils import accuracy
from classification.utils.plots import show_confusion_matrix

from datetime import datetime

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
        # print(line)
        return None


def reader(port=None):
    ser = serial.Serial(port=port, baudrate=115200)
    while True:
        line = ""
        while not line.endswith("\n"):
            line += ser.read_until(b"\n", size=2 * N_MELVECS * MELVEC_LENGTH).decode(
                "ascii"
            )
            # print(line)
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

        plt.figure(figsize=(4, 3))

        model_dir = "../../classification/data/models/"
        filename = "model_rf_new.pickle"
        model = pickle.load(open(model_dir + filename, "rb"))

        hardcoded_classes = np.repeat(["birds", "chainsaw", "fire", "handsaw", "helicopter"], 5)
        predictions = np.zeros(5*5, dtype=StringDType())
        good_prediction = 0
        for melvec in input_stream:
            now = str(datetime.now()).replace(":", "").replace(" ", "").replace("-","").split(".")[0]
            msg_counter += 1

            mat = np.zeros((2, len(melvec)))
            mat[0] = melvec / np.max(melvec)
            prediction = model.predict(mat)
            predictions[msg_counter-1] = prediction[0]
            proba = model.predict_proba(mat)

            try: good_prediction += prediction[0] == hardcoded_classes[msg_counter-1]
            except: pass

            print(f"MEL Spectrogram #{msg_counter}")
            print(f"Class predicted: {prediction[0]}")
            try:
                print(f"Actual class: {hardcoded_classes[msg_counter-1]}")
                print(f"accuracy: {good_prediction/msg_counter}")
            except: pass
            print(f"\t{proba[0,0]}\t{proba[0,1]}\t {proba[0,2]}\t{proba[0,3]}\t{proba[0,4]}\t")
            print("Proba:\tbirds\tchainsaw fire\thandsaw\thelicopter")
            plot_specgram(
                melvec.reshape((N_MELVECS, MELVEC_LENGTH)).T,
                ax=plt.gca(),
                is_mel=True,
                title=f"MEL Spectrogram #{msg_counter}",
                xlabel="Mel vector",
            )
            plt.tight_layout()
            plt.draw()
            # plt.savefig(f"data/melspecgram_fig/wired/{now}_run_{msg_counter}_predicted_{prediction[0]}.pdf")
            # plt.savefig(f"data/melspecgram_fig/miced/{now}_run_{msg_counter}_predicted_{prediction[0]}.pdf")
            plt.pause(1)
            plt.clf()

            if msg_counter == 25:
                acc = accuracy(predictions, hardcoded_classes)
                print(f"Accuracy of {filename}: {100 * acc:.1f}%")
                show_confusion_matrix(predictions, hardcoded_classes, ["birds", "chainsaw", "fire", "handsaw", "helicopter"])

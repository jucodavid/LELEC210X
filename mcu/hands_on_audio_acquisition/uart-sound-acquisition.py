"""
uart-reader.py
ELEC PROJECT - 210x
"""

import argparse

import matplotlib.pyplot as plt
import numpy as np
import serial
import soundfile as sf
import pickle
from serial.tools import list_ports

PRINT_PREFIX = "SND:HEX:"
FREQ_SAMPLING = 10200
VAL_MAX_ADC = 4096
VDD = 3.3


def parse_buffer(line):
    line = line.strip()
    if line.startswith(PRINT_PREFIX):
        return bytes.fromhex(line[len(PRINT_PREFIX) :])
    else:
        print(line)
        return None


def reader(port=None):
    ser = serial.Serial(port=port, baudrate=230400)
    while True:
        line = ""
        while not line.endswith("\n"):
            line += ser.read_until(b"\n", size=1042).decode("ascii")
        line = line.strip()
        buffer = parse_buffer(line)
        if buffer is not None:
            dt = np.dtype(np.uint16)
            dt = dt.newbyteorder("<")
            buffer_array = np.frombuffer(buffer, dtype=dt)

            yield buffer_array


def generate_audio(buf, file_name):
    buf = np.asarray(buf, dtype=np.float64)
    buf = buf - np.mean(buf)
    buf /= max(abs(buf))
    sf.write("audio_files/" + file_name + ".ogg", buf, FREQ_SAMPLING)


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
        plt.figure(figsize=(10, 5))
        input_stream = reader(port=args.port)
        msg_counter = 0

        for msg in input_stream:
            name = input("what is the name of the sound ? : ")

            buffer_size = len(msg)
            print("Buffer size is {}".format(buffer_size))
            times = np.linspace(0, buffer_size - 1, buffer_size) * 1 / FREQ_SAMPLING
            voltage_mV = msg * VDD / VAL_MAX_ADC * 1e3
            try:
                with open("Pickle/sound_list", "rb") as f:
                    sound_list = pickle.load(f)
                    sound_list.append(name)
            except:
                with open("Pickle/sound_list", "wb") as f:
                    sound_list = [name]
                    pickle.dump(sound_list, f)
            with open("Pickle/sound_list", "wb") as f:
                pickle.dump(sound_list, f)
            with open("Pickle/{}".format(name), "wb") as f:
                pickle.dump(msg, f)

            print("Audio successfully pickled!")

            plt.plot(times, voltage_mV)
            plt.title(name)
            plt.xlabel("Time (s)")
            plt.ylabel("Voltage (mV)")
            plt.ylim([0, 3300])
            # plt.draw()
            # plt.pause(0.001)
            # plt.cla()

            generate_audio(msg, name)

            msg_counter += 1
            # begin merde
            plt.show()
            break
            # end merde

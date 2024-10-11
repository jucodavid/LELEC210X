"""
uart-reader.py
ELEC PROJECT - 210x
"""

import argparse

import matplotlib.pyplot as plt
import numpy as np
import serial
import soundfile as sf
from serial.tools import list_ports
# from playsound import playsound
from matplotlib.ticker import EngFormatter
formatter_s = EngFormatter(unit='s', usetex=True)
formatter_dB = EngFormatter(unit='dB', usetex=True)
formatter_Hz = EngFormatter(unit='Hz', usetex=True)

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
    ser = serial.Serial(port=port, baudrate=115200)
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
    # plt.ion()
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
            print(f"Acquisition #{msg_counter}")

            buffer_size = len(msg)
            times = np.linspace(0, buffer_size - 1, buffer_size) * 1 / FREQ_SAMPLING
            voltage_mV = msg * VDD / VAL_MAX_ADC * 1e3

            ax1 = plt.subplot(211)
            ax1.plot(times, voltage_mV)
            ax1.set_xlabel("Time (s)")
            ax1.set_ylabel("Voltage (mV)")
            ax1.set_ylim([0, 3300])
            ax1.xaxis.set_major_formatter(formatter_s)

            ax2 = plt.subplot(212)
            ft = np.fft.fft(voltage_mV)
            ft = np.fft.fftshift(ft)
            freqs = np.fft.fftfreq(buffer_size, 1 / FREQ_SAMPLING)
            freqs = np.fft.fftshift(freqs)
            ax2.set_xlabel("Frequency (Hz)")
            ax2.set_ylabel("Magnitude")
            freqs = freqs[buffer_size//2:]
            ft = ft[buffer_size//2:]
            ax2.plot(freqs, np.abs(ft))
            ax2.set_yscale('log')
            ax2.grid(True)
            ax2.xaxis.set_ticks(np.arange(0, 5000, 200))
            ax2.xaxis.set_major_formatter(formatter_Hz)
            ax2.tick_params(axis='x', labelrotation=90)

            plt.suptitle(f"Acquisition #{msg_counter}")
            plt.tight_layout()
            plt.draw()
            plt.pause(5)
            ax1.cla()
            ax2.cla()

            generate_audio(msg, f"acq-{msg_counter}")
            print("generated audio\n")
            # playsound(f"acq-{msg_counter}")

            msg_counter += 1

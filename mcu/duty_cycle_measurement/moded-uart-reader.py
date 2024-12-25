"""
uart-reader.py
ELEC PROJECT - 210x
"""

import argparse
import numpy as np
import serial
from serial.tools import list_ports

steps_individual_cycle = np.zeros((9,20))
steps_cycle = [[],[],[],[],[],[],[],[],[],[]]
FV_individual_cycle = []
Total_FV_cycle = []
FV_cycle = []
ENCODE_cycle = []
WFI_RADIO_individual_cycle = []
WFI_RADIO_cycle = []
RADIO_cycle = []
COUNT = 0
Nmelvec = 0
step_name = ["0.1", "0.2", "1", "2", "3.1", "3.2", "3.3", "3.4", "4"]

argParser = argparse.ArgumentParser()
argParser.add_argument("-p", "--port", help="Port for serial communication")
args = argParser.parse_args()
print("basic-uart-reader launched...\n")

if args.port is None:
    print("No port specified, here is a list of serial communication port available")
    print("================")
    port = list(list_ports.comports())
    for p in port:
        print(p.device)
    print("================")
    print("Launch this script with [-p PORT_REF] to access the communication port")
else:
    serialPort = serial.Serial(
        port=args.port,
        baudrate=115200,
        bytesize=8,
        timeout=2,
        stopbits=serial.STOPBITS_ONE,
    )
    serialString = ""  # Used to hold data coming over UART
    while 1:
        # Wait until there is data waiting in the serial buffer
        if serialPort.in_waiting > 0:
            # Read data out of the buffer until a carraige return / new line is found
            serialString = serialPort.readline()

            # Print the contents of the serial data
            try:
                s = serialString.decode("Ascii").strip()
                print(s.strip())
                if s == "[S2LP] Packet transmitted!":
                    continue
                elif s[7:10] == "0.1":
                    steps_individual_cycle[0][Nmelvec] = int(s[11:-7])
                elif s[7:10] == "0.2":
                    steps_individual_cycle[1][Nmelvec] = int(s[11:-7])
                elif s[7:8]  == "1":
                    steps_individual_cycle[2][Nmelvec] = int(s[9:-7])
                elif s[7:8]  == "2":
                    steps_individual_cycle[3][Nmelvec] = int(s[9:-7])
                elif s[7:10] == "3.1":
                    steps_individual_cycle[4][Nmelvec] = int(s[11:-7])
                elif s[7:10] == "3.2":
                    steps_individual_cycle[5][Nmelvec] = int(s[11:-7])
                elif s[7:10] == "3.3":
                    steps_individual_cycle[6][Nmelvec] = int(s[11:-7])
                elif s[7:10] == "3.4":
                    steps_individual_cycle[7][Nmelvec] = int(s[11:-7])
                elif s[7:8]  == "4":
                    steps_individual_cycle[8][Nmelvec] = int(s[9:-7])
                    Nmelvec += 1
                elif s[0:19] == "[PERF] Computed FV ":
                    FV_individual_cycle.append(int(s[19:-7]))
                elif s[0:16] == "[PERF] Total FV ":
                    Total_FV_cycle.append(int(s[16:-7]))
                elif s[0:21] == "[PERF] Encode packet ":
                    ENCODE_cycle.append(int(s[21:-7]))
                elif s[0:17] == "[PERF] Radio WFI ":
                    WFI_RADIO_individual_cycle.append(int(s[17:-7]))
                elif s[0:19] == "[PERF] Send packet ":
                    RADIO_cycle.append(int(s[19:-7]))

                    COUNT += 1

                    print("=========================================")
                    print("COUNT: ", COUNT)

                    for i in range(9):
                        steps_cycle[i].append(np.mean(np.array(steps_individual_cycle[i])))
                        print("STEP", step_name[i], ": ", np.mean(np.array(steps_cycle[i])))

                    FV_cycle.append(np.sum(np.array(FV_individual_cycle)))
                    FV_individual_cycle = []
                    print("FV: ", np.mean(np.array(FV_cycle)))

                    print("TOTAL FV: ", np.mean(np.array(Total_FV_cycle)))

                    print("ENCODE: ", np.mean(np.array(ENCODE_cycle)))

                    WFI_RADIO_cycle.append(np.sum(np.array(WFI_RADIO_individual_cycle)))
                    WFI_RADIO_individual_cycle = []
                    print("WFI_RADIO: ", np.mean(np.array(WFI_RADIO_cycle)))

                    print("RADIO: ", np.mean(np.array(RADIO_cycle)))
                    print("=========================================")
            except:
                pass


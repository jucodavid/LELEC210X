from typing import Optional

import numpy as np

BIT_RATE = 50e3
PREAMBLE = np.array([int(bit) for bit in f"{0xAAAAAAAA:0>32b}"])
SYNC_WORD = np.array([int(bit) for bit in f"{0x3E2A54B7:0>32b}"])


class Chain:
    name: str = ""

    # Communication parameters
    bit_rate: float = BIT_RATE
    freq_dev: float = BIT_RATE / 4

    osr_tx: int = 64
    osr_rx: int = 8

    preamble: np.ndarray = PREAMBLE
    sync_word: np.ndarray = SYNC_WORD

    payload_len: int = 100 # Number of bits per packet   HERE <---- payload length = 8*100 dans stm32

    # Simulation parameters
    n_packets: int = 500  # Number of sent packets      HERE <----200 (pour le fun)

    # Channel parameters
    sto_val: float = 0
    sto_range: float = 10 / BIT_RATE  # defines the delay range when random

    cfo_val: float = 0
    cfo_range: float = (
        1000  # defines the CFO range when random (in Hz) #(1000 in old repo)
    )

    snr_range: np.ndarray = np.arange(-10, 25)

    # Lowpass filter parameters
    numtaps: int = 31
    cutoff: float = BIT_RATE * osr_rx / 6.0001  # or 2*BIT_RATE,...     HERE <----

    # Tx methods

    def modulate_fsk(self, bits: np.array) -> np.array:
        """
        Modulates a stream of bits of size N
        with a given TX oversampling factor R (osr_tx).

        Uses Continuous-Phase FSK modulation.

        :param bits: The bit stream, (N,).
        :return: The modulates bit sequence, (N * R,).
        """
        fd = self.freq_dev  # Frequency deviation, Delta_f
        B = self.bit_rate  # B=1/T
        h = 2 * fd / B  # Modulation index
        R = self.osr_tx  # Oversampling factor

        x = np.zeros(len(bits) * R, dtype=np.complex64)
        ph = 2 * np.pi * fd * (np.arange(R) / R) / B  # Phase of reference waveform

        phase_shifts = np.zeros(
            len(bits) + 1
        )  # To store all phase shifts between symbols
        phase_shifts[0] = 0  # Initial phase

        for i, b in enumerate(bits):
            x[i * R : (i + 1) * R] = np.exp(1j * phase_shifts[i]) * np.exp(
                1j * (1 if b else -1) * ph
            )  # Sent waveforms, with starting phase coming from previous symbol
            phase_shifts[i + 1] = phase_shifts[i] + h * np.pi * (
                1 if b else -1
            )  # Update phase to start with for next symbol

        return x

    def modulate(self, bits: np.array) -> np.array:
        """
        Modulates a stream of bits using BPSK modulation.

        :param bits: The bit stream, (N,).
        :return: The modulated bit sequence, (N * R,).
        """
        R = self.osr_tx  # Oversampling factor
        B = self.bit_rate  # Bit rate

        x = np.zeros(len(bits) * R, dtype=np.complex64)
        for i, b in enumerate(bits):
            x[i * R : (i + 1) * R] = (1 if b else -1) * np.ones(R, dtype=np.complex64)

        return x

    def demodulate(self, y: np.array) -> np.array:
        """
        Demodulates a BPSK modulated signal.

        :param y: The received signal, (N * R,).
        :return: The demodulated bit stream, (N,).
        """
        R = self.osr_rx  # Receiver oversampling factor
        nb_syms = len(y) // R  # Number of symbols

        # Reshape the received signal to group samples of each symbol together
        y = np.resize(y, (nb_syms, R))

        # Integrate over each symbol period and make a decision based on the sign
        bits_hat = (np.sum(y, axis=1) > 0).astype(int)

        #bits_hat = np.zeros(nb_syms, dtype=int)
        #for i in range(nb_syms):
        #    bits_hat[i] = 1 if np.sum(y[i]) > 0 else 0

        return bits_hat

    # Rx methods
    bypass_preamble_detect: bool = True

    def preamble_detect(self, y):
        """
        Detect a preamble computing the received energy (average on a window).
        """
        L = 4 * self.osr_rx
        y_abs = np.abs(y)

        for i in range(0, int(len(y) / L)):
            sum_abs = np.sum(y_abs[i * L : (i + 1) * L])
            if sum_abs > (L - 1):  # fix threshold
                return i * L

        return None

    #bypass_cfo_estimation = False
    bypass_cfo_estimation = True                                                 #HERE <----

    def cfo_estimation(self, y):
        """
        Estimates CFO using Moose algorithm, on first samples of preamble.
        """
        # TO DO: extract 2 blocks of size N*R at the start of y
        N = 6 # 2 ou 6
        Nt = N * self.osr_rx
        T = 1 / self.bit_rate
        # TO DO: apply the Moose algorithm on these two blocks to estimate the CFO
        """sum = 0
        for i in range(Nt):
            sum += y[i+Nt] * np.conj(y[i])
        cfo_est = np.angle(sum) / (2 * np.pi * Nt/self.osr_rx/self.bit_rate)"""
        sum_est = np.vdot(y[:Nt], y[Nt:2*Nt])
        cfo_est = np.angle(sum_est) / (2 * np.pi * Nt * T/self.osr_rx)
        #cfo_est = 0  # Default value, to change

        return cfo_est

    bypass_sto_estimation = True                                                 #HERE <----

    def sto_estimation(self, y):
        """
        Estimates symbol timing (fractional) based on phase shifts.
        """
        R = self.osr_rx

        # Computation of derivatives of phase function
        phase_function = np.unwrap(np.angle(y))
        phase_derivative_1 = phase_function[1:] - phase_function[:-1]
        phase_derivative_2 = np.abs(phase_derivative_1[1:] - phase_derivative_1[:-1])

        sum_der_saved = -np.inf
        save_i = 0
        for i in range(0, R):
            sum_der = np.sum(phase_derivative_2[i::R])  # Sum every R samples

            if sum_der > sum_der_saved:
                sum_der_saved = sum_der
                save_i = i

        return np.mod(save_i + 1, R)

    def demodulate_fsk(self, y):
        """
        Non-coherent demodulator.
        """
        R = self.osr_rx  # Receiver oversampling factor
        nb_syms = len(y) // R  # Number of CPFSK symbols in y

        # Group symbols together, in a matrix. Each row contains the R samples over one symbol period
        y = np.resize(y, (nb_syms, R))
        # print(y)
        # TO DO: generate the reference waveforms used for the correlation
        # hint: look at what is done in modulate() in chain.py

        eS0 = np.exp(-2j * np.pi * self.freq_dev * np.arange(R) / self.bit_rate / R)
        eS1 = np.exp( 2j * np.pi * self.freq_dev * np.arange(R) / self.bit_rate / R)

        # TO DO: compute the correlations with the two reference waveforms (r0 and r1)
        #bits_hat = np.zeros(nb_syms, dtype=int)  # Default value, all bits=0. TO CHANGE!

        r0 = np.abs(np.dot(y, eS1)) / R
        r1 = np.abs(np.dot(y, eS0)) / R
        bits_hat = (r1 > r0).astype(int)

        return bits_hat


class BasicChain(Chain):
    name = "Basic Tx/Rx chain"

    cfo_val, sto_val = np.nan, np.nan  # CFO and STO are random

    bypass_preamble_detect = False                                                  #HERE <----

    def preamble_detect(self, y):
        """
        Detect a preamble computing the received energy (average on a window).
        """
        L = 4 * self.osr_rx
        y_abs = np.abs(y)

        for i in range(0, int(len(y) / L)):
            sum_abs = np.sum(y_abs[i * L : (i + 1) * L])
            if sum_abs > (L - 1):  # fix threshold
                return i * L

        return None

    #bypass_cfo_estimation = False
    bypass_cfo_estimation = True                                                 #HERE <----

    def cfo_estimation(self, y):
        """
        Estimates CFO using Moose algorithm, on first samples of preamble.
        """
        # TO DO: extract 2 blocks of size N*R at the start of y
        N = 2
        Nt = N * self.osr_rx
        T = 1 / self.bit_rate
        # TO DO: apply the Moose algorithm on these two blocks to estimate the CFO
        """sum = 0
        for i in range(Nt):
            sum += y[i+Nt] * np.conj(y[i])
        cfo_est = np.angle(sum) / (2 * np.pi * Nt/self.osr_rx/self.bit_rate)"""
        sum_est = np.vdot(y[:Nt], y[Nt:2*Nt])
        cfo_est = np.angle(sum_est) / (2 * np.pi * Nt * T/self.osr_rx)
        #cfo_est = 0  # Default value, to change

        return cfo_est

    bypass_sto_estimation = False                                                 #HERE <----

    def sto_estimation(self, y):
        """
        Estimates symbol timing (fractional) based on phase shifts.
        """
        R = self.osr_rx

        # Computation of derivatives of phase function
        phase_function = np.unwrap(np.angle(y))
        phase_derivative_1 = phase_function[1:] - phase_function[:-1]
        phase_derivative_2 = np.abs(phase_derivative_1[1:] - phase_derivative_1[:-1])

        sum_der_saved = -np.inf
        save_i = 0
        for i in range(0, R):
            sum_der = np.sum(phase_derivative_2[i::R])  # Sum every R samples

            if sum_der > sum_der_saved:
                sum_der_saved = sum_der
                save_i = i

        return np.mod(save_i + 1, R)

    def demodulate(self, y):
        """
        Non-coherent demodulator.
        """
        R = self.osr_rx  # Receiver oversampling factor
        nb_syms = len(y) // R  # Number of CPFSK symbols in y

        # Group symbols together, in a matrix. Each row contains the R samples over one symbol period
        y = np.resize(y, (nb_syms, R))
        # print(y)
        # TO DO: generate the reference waveforms used for the correlation
        # hint: look at what is done in modulate() in chain.py

        eS0 = np.exp(-2j * np.pi * self.freq_dev * np.arange(R) / self.bit_rate / R)
        eS1 = np.exp( 2j * np.pi * self.freq_dev * np.arange(R) / self.bit_rate / R)

        # TO DO: compute the correlations with the two reference waveforms (r0 and r1)
        #bits_hat = np.zeros(nb_syms, dtype=int)  # Default value, all bits=0. TO CHANGE!

        r0 = np.abs(np.dot(y, eS1)) / R
        r1 = np.abs(np.dot(y, eS0)) / R
        bits_hat = (r1 > r0).astype(int)

        return bits_hat

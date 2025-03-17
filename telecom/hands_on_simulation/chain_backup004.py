from typing import Optional

import numpy as np

BIT_RATE = 50e3
PREAMBLE = np.array([int(bit) for bit in f"{0xAAAAAAAA:0>32b}"])
SYNC_WORD = np.array([int(bit) for bit in f"{0x3E2A54B7:0>32b}"])


class Chain:
    name: str = ""

    # Communication parameters
    bit_rate: float = BIT_RATE
    freq_dev: float = BIT_RATE / 2

    osr_tx: int = 64
    osr_rx: int = 8

    preamble: np.ndarray = PREAMBLE
    sync_word: np.ndarray = SYNC_WORD

    payload_len: int = 100 # Number of bits per packet   HERE <---- payload length = 8*100 dans stm32

    # Simulation parameters
    n_packets: int = 800  # Number of sent packets      HERE <----200 ou 800(pour le fun)

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

    def modulate(self, bits: np.array) -> np.array:
        """
        Modulates a stream of bits of size N
        with a given TX oversampling factor R (osr_tx).

        Uses Binary Phase Shift Keying (BPSK) in baseband.

        :param bits: The bit stream, (N,).
        :return: The modulated baseband signal, (N * R,).
        """
        R = self.osr_tx  # Oversampling factor

        # Map bits to symbols: 1 -> +1, 0 -> -1
        symbols = np.where(bits == 1, 1.1, -1.1)

        # Upsample the symbols by repeating each symbol R times
        x = np.repeat(symbols, R)

        return x

    def demodulate(self, y: np.array) -> np.array:
        """
        Demodulates a baseband BPSK signal.

        :param y: The received baseband signal, (N * R,).
        :return: The demodulated bit stream, (N,).
        """
        R = self.osr_rx  # Receiver oversampling factor
        nb_syms = len(y) // R  # Number of BPSK symbols in y

        # Group symbols together, in a matrix. Each row contains the R samples over one symbol period
        y = np.resize(y, (nb_syms, R))

        # Average over each symbol period to reduce noise
        symbol_estimates = np.mean(y, axis=1)

        # Decision: if the average is positive, bit is 1; else, bit is 0
        bits_hat = (symbol_estimates > 0).astype(int)

        return bits_hat


    def modulate_fsk_coh(self, bits: np.array) -> np.array:
        """
        Modulates a stream of bits of size N
        with a given TX oversampling factor R (osr_tx).

        Uses Binary Phase Shift Keying (BPSK) modulation.

        :param bits: The bit stream, (N,).
        :return: The modulated bit sequence, (N * R,).
        """
        R = self.osr_tx  # Oversampling factor
        t = np.arange(R) / (self.bit_rate * R)  # Time vector for one symbol period
        carrier = np.cos(2 * np.pi * self.freq_dev/2 * t)  # Carrier signal

        # Modulate each bit
        x = np.zeros(len(bits) * R, dtype=np.complex64)
        for i, b in enumerate(bits):
            x[i * R : (i + 1) * R] = (1 if b else -1) * carrier

        return x

    def demodulate_fsk_coh(self, y: np.array) -> np.array:
        """
        Demodulates a BPSK signal.

        :param y: The received signal, (N * R,).
        :return: The demodulated bit stream, (N,).
        """
        R = self.osr_rx  # Receiver oversampling factor
        nb_syms = len(y) // R  # Number of BPSK symbols in y

        # Group symbols together, in a matrix. Each row contains the R samples over one symbol period
        y = np.resize(y, (nb_syms, R))

        # Generate the reference carrier signal
        t = np.arange(R) / (self.bit_rate * R)
        carrier = np.cos(2 * np.pi * self.freq_dev/2 * t)

        # Correlate each symbol with the carrier
        correlations = np.sum(y * carrier, axis=1) / R

        # Decision: if correlation is positive, bit is 1; else, bit is 0
        bits_hat = (correlations > 0).astype(int)

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


    def cfo_estimation_fft(self, y):
        """
        Estimates CFO using a zero-padded FFT method, with IFFT to refine the CFO estimation.
        """

        # Paramètres
        N = 16  # Taille du bloc
        Nt = N * self.osr_rx  # Nombre d'échantillons dans chaque bloc
        T = 1 / self.bit_rate  # Période du symbole

        # Extraire les deux blocs de taille Nt
        block1 = y[:Nt]
        block2 = y[Nt:2*Nt]
        
        # Appliquer un zero padding sur les blocs pour améliorer la résolution en fréquence
        padding_size = 4096*2**3  # Taille de padding pour FFT (peut être ajustée)
        block1_padded = np.pad(block1, (0, padding_size - len(block1)), mode='constant')
        block2_padded = np.pad(block2, (0, padding_size - len(block2)), mode='constant')
        
        # Calculer la FFT des deux blocs zéro-padded
        fft_block1 = np.fft.fft(block1_padded)
        fft_block2 = np.fft.fft(block2_padded)
        
        # Trouver l'index de la fréquence maximale dans le domaine fréquentiel
        #freq_diff = np.angle(np.vdot(fft_block1, fft_block2))  # Calcul de la phase sur les deux blocs en fréquence
        ifft_block1 = np.fft.ifft(fft_block1)
        ifft_block2 = np.fft.ifft(fft_block2)
        freq_diff = np.vdot(ifft_block1, ifft_block2)  # Calcul de la phase sur les deux blocs en temporel
        
        # Estimer le CFO sur base de la différence de phase à la fréquence maximale
        cfo_est = np.angle(freq_diff) / (2 * np.pi * Nt * T / self.osr_rx)

        return cfo_est


    def cfo_estimation_Moose(self, y):
        """
        Estimates CFO using Moose algorithm, on first samples of preamble.
        """
        # TO DO: extract 2 blocks of size N*R at the start of y
        N = 8 # 2 ou 6
        Nt = N * self.osr_rx
        T = 1 / self.bit_rate
        # TO DO: apply the Moose algorithm on these two blocks to estimate the CFO
        sum_est = np.vdot(y[:Nt], y[Nt:2*Nt])
        cfo_est = np.angle(sum_est) / (2 * np.pi * Nt * T/self.osr_rx)
        #cfo_est = 0  # Default value, to change

        return cfo_est

    
    def cfo_estimation(self, y) -> float:
        """
        Estimates CFO using Moose algorithm, averaging over multiple block pairs.

        :param y: Received signal (preamble part).
        :param N: Block size (in symbols).
        :param L: Length of the preamble to consider (in symbols).
        :param D: Maximum distance between blocks (in symbols).
        :return: Averaged CFO estimate.
        """
        R = self.osr_rx  # Receiver oversampling factor
        T = 1 / self.bit_rate  # Symbol period

        N = 6       #default 6
        L = 32      #default 32
        D = 4       #default 2
        # Convert block size and preamble length to samples
        Nt = N * R  # Block size in samples
        Lt = L * R  # Preamble length to consider in samples
        Dt = D * R  # Maximum distance between blocks in samples

        # Ensure the preamble length is sufficient
        if Lt > len(y):
            raise ValueError("Preamble length L is larger than the received signal.")

        # Extract the relevant part of the preamble
        y_preamble = y[:Lt]

        # Initialize a list to store CFO estimates
        cfo_estimates = []

        for k in range(2,11,2):
            N = k
            Nt = N * R
            # Iterate over all possible pairs of blocks
            for i in range(0, Lt - 2*Nt+1,R):  # Start of first block
                for j in range(i + Nt, min(i + Nt + Dt, Lt - Nt + 1),2*R):  # Start of second block
                    # Extract the two blocks
                    block1 = y_preamble[i:i + Nt]
                    block2 = y_preamble[j:j + Nt]

                    # Apply the Moose algorithm
                    sum_est = np.vdot(block1, block2)
                    cfo_est = np.angle(sum_est) / (2 * np.pi * (j - i) * T / R)

                    # Store the CFO estimate
                    cfo_estimates.append(cfo_est)

        # Average the CFO estimates
        if len(cfo_estimates) == 0:
            raise ValueError("No valid block pairs found for CFO estimation.")

        avg_cfo_est = np.mean(cfo_estimates)
        return avg_cfo_est

    def cfo_estimation__fft(self, y):        #par fft
        """
        Estimates CFO using a frequency domain method (FFT-based).
        This approach works well when the signal is coherent and has well-defined frequency components.
        """
        R = self.osr_rx  # Oversampling factor for receiver
        N = 16 # 2 ou 6
        Nt = N * self.osr_rx
        T = 1 / self.bit_rate
        fs = self.bit_rate * R  # Sampling frequency
        #N = len(y)  # Length of the received signal
        zero_pad_factor = 2**4  # Increase zero-padding factor for finer resolution
        fft_size = Nt*zero_pad_factor  # FFT size, can be adjusted based on signal length
        signal = np.pad(y[:Nt], (0, fft_size - Nt), mode='constant')

        # Perform FFT on the received signal
        Y_fft = np.fft.fft(signal, fft_size)
        # Find the peak in the frequency spectrum and calculate the CFO
        freq_bins = np.fft.fftfreq(fft_size, fs**-1)
        peak_bin = np.argmax(np.abs(Y_fft))

        # Estimate CFO based on the peak frequency bin
        cfo_est = freq_bins[peak_bin]

        return cfo_est

    bypass_sto_estimation = False                                                 #HERE <----

    def sto_estimation(self, y):
        """
        Estimates symbol timing (fractional) based on phase shifts.
        """
        R = self.osr_rx

        #preamble_length = 32 * R  # Length of the preamble in samples
        #y_preamble = y[:preamble_length]  # Use only the preamble

        # Computation of derivatives of phase function
        phase_function = np.unwrap(np.angle(y))
        #phase_function = np.unwrap(np.angle(y_preamble))
        
        phase_derivative_1 = phase_function[2:] - phase_function[:-2]
        #phase_derivative_1 = np.diff(phase_function)
        phase_derivative_2 = np.abs(phase_derivative_1[1:] - phase_derivative_1[:-1])
        #phase_derivative_2 = np.abs(np.diff(phase_derivative_1))

        sum_der_saved = -np.inf
        save_i = 0
        for i in range(0, R):
            #sum_der = np.sum(phase_derivative_2[i::R])  # Sum every R samples
            sum_der = (
                np.sum(phase_derivative_2[max(i - 2, 0)::R]) +  # i-2
                np.sum(phase_derivative_2[max(i - 1, 0)::R]) +  # i-1
                np.sum(phase_derivative_2[i::R]) +  # i
                np.sum(phase_derivative_2[min(i + 1, R - 1)::R])+  # i+1
                np.sum(phase_derivative_2[min(i + 2, R - 1)::R])  # i+2
            )

            if sum_der > sum_der_saved:
                sum_der_saved = sum_der
                save_i = i

        return np.mod(save_i + 1, R)

    def modulate_fsk_noncoh(self, bits: np.array) -> np.array:
        """
        Modulates a stream of bits of size N
        with a given TX oversampling factor R (osr_tx).

        Uses Continuous-Phase FSK modulation.

        :param bits: The bit stream, (N,).
        :return: The modulates bit sequence, (N * R,).
        """
        fd = self.freq_dev  # Frequency deviation, Delta_f
        B = self.bit_rate  # B=1/T
        h = 2 * fd / B  # Modulation index, freq_dev / bit_rate = 1/4 changé à 1/2
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

    def demodulate_fsk_noncoh(self, y):
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

        r0 = np.abs(np.dot(y, eS1))
        r1 = np.abs(np.dot(y, eS0)) 
        bits_hat = (r1 > r0).astype(int)

        return bits_hat

    def modulate_fsk_coh(self, bits: np.array) -> np.array:
        """
        Modulates a stream of bits of size N
        with a given TX oversampling factor R (osr_tx).

        Uses Continuous-Phase FSK modulation.

        :param bits: The bit stream, (N,).
        :return: The modulates bit sequence, (N * R,).
        """
        fd = self.freq_dev  # Frequency deviation, Delta_f
        B = self.bit_rate  # B=1/T
        R = self.osr_tx  # Oversampling factor

        x = np.zeros(len(bits) * R, dtype=np.complex64)
        ph = 2 * np.pi * fd * (np.arange(R) / R) / B  # Phase of reference waveform

        for i, b in enumerate(bits):
            x[i * R : (i + 1) * R] = np.exp(1j * (1 if b else -1) * ph)  # Sent waveforms, with starting phase coming from previous symbol
        return x

    def demodulate_fsk_coh(self, y):
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

        r0 = np.real(np.dot(y, eS1))
        r1 = np.real(np.dot(y, eS0)) 
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

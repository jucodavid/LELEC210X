import scipy.io
import matplotlib.pyplot as plt
import numpy as np
import h5py

filename = 'measures_recordings.mat'
data = np.fromfile(filename, dtype=complex)
freq = 50e3*8
amplitude = np.abs(data)

def plot_complex(data):
    plt.figure(figsize=(10, 6))
    plt.plot(data.real, data.imag, 'o')
    plt.title('Complex Data Plot')
    plt.xlabel('Real Part')
    plt.ylabel('Imaginary Part')
    plt.grid(True)
    plt.show()

def plot_amplitude(data):
    plt.figure(figsize=(10, 6))
    plt.plot(np.abs(data))
    plt.title('Absolute Value of Complex Data')
    plt.xlabel('Index')
    plt.ylabel('Magnitude')
    plt.grid(True)
    plt.show()

def my_FFT(signal, freq): 
    FFT0        = np.abs(np.fft.fft(signal))
    frequencies = np.fft.fftfreq(signal.shape[-1], d=1/freq)
    frequencies = frequencies[1:int(FFT0.shape[-1]/2)]
    FFT         = FFT0[1:int(FFT0.shape[-1]/2)]
    return FFT, frequencies

def plot_fft(signal, freq):
    FFT, frequencies = my_FFT(signal, freq)
    plt.figure(figsize=(10, 6))
    plt.plot(frequencies, FFT)
    plt.title('FFT of Signal')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.grid(True)
    plt.show()

def plot_fft_db(signal, freq):
    FFT, frequencies = my_FFT(signal, freq)
    plt.figure(figsize=(10, 6))
    plt.plot(frequencies, 20*np.log10(FFT))
    plt.title('FFT of Signal in dB')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude (dB)')
    plt.grid(True)
    plt.show()

data_no_agc = np.fromfile('record_capture_10-20-40-60-2.mat', dtype=complex)

print("Data shape:", data.shape)
print("Data type:", data_no_agc.shape)

"""
plot_amplitude(data)
plot_complex(data)
plot_fft(data, freq)
plot_fft_db(data, freq)
"""
plot_amplitude(data_no_agc)
plot_complex(data_no_agc)
plot_fft(data_no_agc, freq)
plot_fft_db(data_no_agc, freq)
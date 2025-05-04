import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def plot_ber_vs_snr(df, a, mini, maxi):
    """
    Function to plot Bit Error Rate (BER) versus Signal-to-Noise Ratio (SNR),
    with the SNR divided into a specified number of bins.
    
    Parameters:
    df (DataFrame): DataFrame containing 'SNR' and 'INVALID' columns.
    a (int): Number of bins to divide the SNR range into.
    mini (float): Minimum SNR value for binning.
    maxi (float): Maximum SNR value for binning.
    """
    df = df[(df['SNR'] >= mini) & (df['SNR'] <= maxi)]
    snr_min = df['SNR'].min()
    snr_max = df['SNR'].max()
    bins = np.linspace(snr_min, snr_max, a+1)
    
    # Digitize the SNR values into bins
    #df['SNR_bin'] = np.digitize(df['SNR'], bins) - 1
    df['SNR_bin'] = pd.cut(df['SNR'], bins, include_lowest=True)
    
    # Calculate the mean INVALID value for each bin
    ber_data = df.groupby('SNR_bin')['BER'].mean()
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    
    print(bin_centers)
    print(ber_data.values)
    # Plot BER vs. SNR
    plt.figure(figsize=(10, 6))
    plt.plot(bin_centers, ber_data.values, 'o-', label='BER')
    plt.xlabel('SNR (dB)')
    plt.ylabel('Bit Error Rate (BER)')
    plt.yscale('log')
    plt.title(f'BER vs. SNR (a={a})')
    plt.legend()
    plt.grid(True)
    plt.show()

fields_names = ['CFO', 'STO', 'SNR', 'TXP', 'BER', 'INVALID']
#ber_data = pd.read_csv('Measures_Q1/PER-SNR.csv', sep=',',skiprows=1, names=fields_names)
ber_data = pd.read_csv('measures_df.csv', sep=',',skiprows=1, names=fields_names)
plot_ber_vs_snr(ber_data, 25, 0, 30)

#for i in range(15,30):
    #plot_ber_vs_snr(ber_data, i, -0, 30)

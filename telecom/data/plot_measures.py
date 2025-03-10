import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def create_plot(x, y, title, xlabel, ylabel):
    plt.figure()
    plt.plot(x, y, marker='o')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.show()

def plot_SNR_f_vs_f_dBm(f_dBm, fc, SNR_f):
    plt.figure()
    for i, freq in enumerate(fc):
        plt.plot(f_dBm, SNR_f[i], marker='o', label=f'fc = {freq/1e3} kHz')
    plt.title('Low pass filter impact')
    plt.xlabel('Tx power (dBm)')
    plt.ylabel('SNR (dB)')
    plt.legend()
    plt.grid(True)
    plt.show()

def merge_files(file1_path, file2_path, output_file_path):
    with open(file1_path, 'r') as file1, open(file2_path, 'r') as file2, open(output_file_path, 'w') as output_file:
        for line in file1:
            output_file.write(line)
        for line in file2:
            output_file.write(line)

def plot_per_vs_snr(df):
    """
    Function to plot Packet Error Rate (PER) versus Signal-to-Noise Ratio (SNR).
    
    Parameters:
    df (DataFrame): DataFrame containing 'snr' and 'invalid' columns.
    """
    # Group by SNR and calculate PER
    per_data = df.groupby('SNR')['INVALID'].mean()
    
    # Plot PER vs. SNR
    plt.figure(figsize=(10, 6))
    plt.plot(per_data.index, per_data.values, 'o-', label='PER')
    plt.xlabel('SNR (dB)')
    plt.ylabel('Packet Error Rate (PER)')
    plt.yscale('log')
    plt.title('PER vs. SNR')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_per_vs_snr2(df, a,mini,maxi):
    """
    Function to plot Packet Error Rate (PER) versus Signal-to-Noise Ratio (SNR),
    with the SNR divided into a specified number of bins.
    
    Parameters:
    df (DataFrame): DataFrame containing 'SNR' and 'INVALID' columns.
    a (int): Number of bins to divide the SNR range into.
    """
    df = df[(df['SNR'] <= maxi) & (df['SNR'] >= mini)]
    # Define the bin edges for SNR
    snr_min = df['SNR'].min()
    snr_max = df['SNR'].max()
    bins = np.linspace(snr_min, snr_max, a + 1)

    # Bin the SNR values
    df['SNR_bin'] = pd.cut(df['SNR'], bins, include_lowest=True)

    # Group by the bins and calculate the mean PER for each bin
    per_data = df.groupby('SNR_bin')['INVALID'].mean()

    # Calculate the bin centers for plotting
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    print(per_data.values)
    print(bin_centers)
    # Plot PER vs. SNR
    plt.figure(figsize=(10, 6))
    plt.plot(bin_centers, per_data.values, 'o-', label='PER')
    plt.xlabel('SNR (dB)')
    plt.ylabel('Packet Error Rate (PER)')
    plt.yscale('log')
    plt.title(f'PER vs. SNR (with {a} bins)')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_cfo_histogram(df):
    """
    Function to plot the histogram of CFO values from the DataFrame.
    
    Parameters:
    df (DataFrame): DataFrame containing 'CFO' column.
    """
    # Plotting the histogram of CFO
    #df = df[(df['SNR'] <= 20) & (df['SNR'] >= 10)]
    #df = df[(df['CFO'] <= 10000) & (df['CFO'] >= 5000)]
    print(df['CFO'].mean())
    print(df['CFO'].std())
    plt.figure(figsize=(10, 7))
    plt.hist(df['CFO'], bins=150, edgecolor='black')
    plt.xlabel('CFO [Hz]')
    plt.ylabel('N° of occurrences')
    #plt.xlim(1300,1400)
    plt.title('CFO Histogram')
    plt.grid(True)
    plt.show()


x_dist = [1,5,7.5,10,15,20,30,40,50,60,80,100,120]
SNR_dist = [52.4,47.2,43.5,41.6,40.8,39.3,38.2,37.4,36.8,36.1,35.7,35.2,34.9]


f_dBm = [-12,-11,-10,-9,-8,-7,-6,-5,-4,-3,-2,-1,0]
fc = [62.5e3,125e3,200e3]
SNR_f = [[28.5,29.3,29.7,30.7,31.5,32.8,33.6,34.5,35.3,36,37.1,38.1,39.1],
         [28.3,28.7,29.2,30,30.5,31.2,32,32.6,33.5,34.2,35.4,36.2,37.3],
         [29.2,29.5,29.8,30.2,30.6,31.0,31.7,32.4,33.2,33.9,34.9,35.7,36.4]]
fc2 = [62.5e3,125e3]
SNR_f2 = [[28.5,29.3,29.7,30.7,31.5,32.8,33.6,34.5,35.3,36,37.1,38.1,39.1],
         [28.3,28.7,29.2,30,30.5,31.2,32,32.6,33.5,34.2,35.4,36.2,37.3]]

#merge_files('2025_-60_-50_300_001.txt', 'output25_-50_-20.txt', 'output25_-60_-20.txt')

field_names = ['CFO', 'STO', 'SNR', 'TXP', 'BER', 'INVALID']
#per_data = pd.read_csv('PER-SNR-2.csv', sep=',', skiprows=1,names=field_names)
per_data = pd.read_csv('measures_df.csv', sep=',', skiprows=1,names=field_names)
#print(per_data)

plot_per_vs_snr(per_data)
mini,maxi = 0,30
#plot_per_vs_snr2(per_data, 50,15,30)




#create_plot(x_dist, SNR_dist, 'SNR vs Distance', 'Distance (cm)', 'SNR (dB)')
#plot_SNR_f_vs_f_dBm(f_dBm, fc2, SNR_f2)
#for i in range(20,30):
 #   plot_per_vs_snr2(per_data, i,mini, maxi)
plot_per_vs_snr2(per_data, 25,mini, maxi)
plot_cfo_histogram(per_data)





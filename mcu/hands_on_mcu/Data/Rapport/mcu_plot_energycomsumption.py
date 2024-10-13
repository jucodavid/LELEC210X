import numpy as np
import csv
import matplotlib.pyplot as plt

def plot_energy_consumption(csv_file, start_line, graph_title):
    times = []
    channel_1 = []

    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        for _ in range(start_line):
            next(reader)  # Skip lines until start_line
        for row in reader:
            times.append(float(row[1]))
            channel_1.append(float(row[2]))

    plt.figure(figsize=(10, 6))
    #plt.plot(times, np.square(channel_1) / 6.8*1000, label='Channel 1')
    plt.plot(times, np.array(channel_1) / 6.8 * 1000 * 3.3)
    plt.xlabel('Time [s]')
    plt.ylabel('Consumption [mW]')
    plt.title(graph_title)
    #plt.legend()
    plt.grid(True)
    plt.show()

def calculate_plateau_means(csv_file, start_line, plateauxlevels, delta):
    times = []
    channel_1 = []

    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        for _ in range(start_line):
            next(reader)  # Skip lines until start_line
        for row in reader:
            times.append(float(row[1]))
            channel_1.append(3.3*float(row[2]) / 6.8 * 1000)

    plateaus = []
    extreme_times = []
    for level in plateauxlevels:
        plateau_values = [channel_1[i] for i in range(len(channel_1)) if abs(channel_1[i] - level) <= delta]
        plateaus.append(np.mean(plateau_values))
        
        plateau_times = [times[i] for i in range(len(channel_1)) if abs(channel_1[i] - level) <= delta]
        if plateau_times:
            extreme_times.append([min(plateau_times), max(plateau_times)])
        else:
            extreme_times.append([None, None])

    return plateaus, extreme_times

def plot_pie(mean_values, time_extremes):
    # Calculate total consumption for each load
    total_consumptions = []
    for i in range(len(mean_values)):
        if time_extremes[i][0] is not None and time_extremes[i][1] is not None:
            duration = time_extremes[i][1] - time_extremes[i][0]
            total_consumption = mean_values[i] * duration
            total_consumptions.append(total_consumption)
        else:
            total_consumptions.append(0)

    # Plot pie chart
    #labels = [f'Load {i+1}' for i in range(len(mean_values))]
    labels = ['Acquisition', 'Transfer + LED']
    consumption_labels = [f'{total_consumptions[i]:.2f} mWs' for i in range(len(total_consumptions))]
    plt.figure(figsize=(8, 5))
    #plt.pie(total_consumptions, labels=consumption_labels, autopct=lambda p: f'{p:.1f}%\n({p*sum(total_consumptions)/100:.2f} mWs)', startangle=140)
    plt.pie(total_consumptions, labels=consumption_labels, autopct=lambda p: f'{p:.1f}%', startangle=140)
    plt.title('Total Energy Consumption per subtask')
    plt.legend(labels, title="Subtask", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    plt.show()
    

plot_energy_consumption('energy_sequence_2.csv', 9, 'Energy Consumption of the sequence')

mean_values, time_extremes = calculate_plateau_means('energy_sequence_2.csv', 9, [90, 184], 4)
time_extremes[0][1] = time_extremes[1][0]
print("Valeurs moyennes",mean_values)
print("Temps extremes",time_extremes)
plot_pie(mean_values, time_extremes)
print("Duty cycle",(time_extremes[1][1]-time_extremes[1][0])/(time_extremes[1][1]-time_extremes[0][0]))
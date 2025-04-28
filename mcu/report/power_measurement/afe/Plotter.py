import numpy as np
from matplotlib import pyplot as plt
formatterW = plt.matplotlib.ticker.EngFormatter("W")
formatterS = plt.matplotlib.ticker.EngFormatter("s")


GLOBAL_R = 10* 1e3 # Ohm

def read(filename, V):
    n = 0
    b = True
    while b:
        try:
            data = np.loadtxt(filename, delimiter=',', skiprows=n)
            b = False
        except:
            n+=1
    time  = data[:,1]
    power = data[:,2] * (V-data[:,2]) / GLOBAL_R
    return time, power

def average(time, power, xmin, xmax):
    i = 0
    while time[i] < xmin:
        i+=1
    j = 0
    while time[j] < xmax:
        j+=1
    return np.mean(power[i:j])



xmin = 0
xmax = 1.599

time, power = read("afe_3v3_mic.csv", 3.3)
av = average(time, power, xmin, xmax)

fig, ax = plt.subplots(figsize=(10, 5), dpi=120)
ax.set_xlim(xmin, xmax)

ticks = ax.get_xticks()
ax.set_xlabel(f"{formatterS(abs(ticks[0] - ticks[1]))}/div")

ax.yaxis.set_major_formatter(formatterW)
ax.xaxis.set_major_formatter(formatterS)
ax.xaxis.set_ticklabels([])
ax.minorticks_on()

ax.grid(which='major', linewidth='1')
ax.grid(which='minor', linewidth='0.25')

# ax.plot(time, power, label=f"{formatterW(av)}")
time, power = read("afe_3v6_mic_clap.csv", 3.6)
av = average(time, power, xmin, xmax)
ax.plot(time, power, label=f"3.6 V : {formatterW(av)}")

time, power = read("afe_3v3_mic_clap.csv", 3.3)
av = average(time, power, xmin, xmax)
ax.plot(time, power, label=f"3.3 V : {formatterW(av)}")

time, power = read("afe_3v0_mic_clap.csv", 3.0)
av = average(time, power, xmin, xmax)
ax.plot(time, power, label=f"3.0 V : {formatterW(av)}")

time, power = read("afe_2v8_mic_clap.csv", 2.8)
av = average(time, power, xmin, xmax)
ax.plot(time, power, label=f"2.8 V : {formatterW(av)}")

time, power = read("afe_2v5_mic_clap.csv", 2.5)
av = average(time, power, xmin, xmax)
ax.plot(time, power, label=f"2.5 V : {formatterW(av)}")

time, power = read("afe_2v2_mic_clap.csv", 2.2)
av = average(time, power, xmin, xmax)
ax.plot(time, power, label=f"2.2 V : {formatterW(av)}")

time, power = read("afe_2v0_mic_clap.csv", 2.0)
av = average(time, power, xmin, xmax)
ax.plot(time, power, label=f"2.0 V : {formatterW(av)}")

plt.legend(title='Mean Power', framealpha=1)
plt.show()

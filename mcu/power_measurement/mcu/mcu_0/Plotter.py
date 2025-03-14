import numpy as np
from matplotlib import pyplot as plt
formatterW = plt.matplotlib.ticker.EngFormatter("W")
formatterS = plt.matplotlib.ticker.EngFormatter("s")
formatterJ = plt.matplotlib.ticker.EngFormatter("J")


GLOBAL_R = 680 # Ohm

def read(filename):
    n = 0
    b = True
    while b:
        try:
            data = np.loadtxt(filename, delimiter=',', skiprows=n)
            b = False
        except:
            n+=1
    time  = data[:,1]
    power = data[:,2] * (3.3-data[:,2]) / GLOBAL_R
    return time, power

def average(time, power, xmin, xmax):
    i = 0
    while time[i] < xmin:
        i+=1
    j = 0
    while time[j] < xmax:
        j+=1
    return np.mean(power[i:j])




time, power = read("mcu_0.csv")
xmin = 0.175
xmax = 1.45

fig, ax = plt.subplots(figsize=(10, 5), dpi=120)

av = average(time, power, xmin, xmax)
plt.title(f"Total Average Power: {formatterW(av)}")

ax.set_xlim(xmin, xmax)

ticks = ax.get_xticks()
ax.set_xlabel(f"{formatterS(abs(ticks[0] - ticks[1]))}/div")

ax.yaxis.set_major_formatter(formatterW)
ax.xaxis.set_major_formatter(formatterS)
ax.xaxis.set_ticklabels([])
ax.minorticks_on()

ax.grid(which='major', linewidth='1')
ax.grid(which='minor', linewidth='0.25')

ax.plot(time, power, 'k')

tavv = np.zeros(3)
# adc w/ WFI__ & adcto hz to mel
x = xmin + .025
x = [x, x + 1.01]
av = average(time, power, *x)
tavv[0] = av * (x[1] - x[0])
ax.hlines(av, *x, label=f"{formatterW(av)}", color='tab:blue')

# packetisation
x = [x[1], x[1] + .0925]
av = average(time, power, *x)
tavv[1] = av * (x[1] - x[0])
ax.hlines(av, *x, label=f"{formatterW(av)}", color='tab:green')

# radio w/ WFI__
x = [x[1], x[1] + .135]
av = average(time, power, *x)
tavv[2] = av * (x[1] - x[0])
ax.hlines(av, *x, label=f"{formatterW(av)}", color='tab:red')

plt.legend(title='Mean Power', framealpha=1)
# plt.show()

tavlab = np.array([
    f"{formatterJ(tavv[0])}",
    f"{formatterJ(tavv[1])}",
    f"{formatterJ(tavv[2])}",
    # f"{formatterJ(tavv[3])}",
    # f"{formatterJ(tavv[4])}"
    ])

labels = [
    "Sampling & Spectrogram",
    # "Prints",
    "Packetisation",
    "Radio Transmission",
    # "Hex Encoding & Prints"
    ]

fig, ax = plt.subplots(figsize=(7,4) , dpi=120, constrained_layout=True)
ax.pie(tavv, labels=tavlab, autopct='%1.1f%%')
plt.legend(labels, title='Mean Energy', framealpha=1, bbox_to_anchor=(1.04, 1))
plt.show()

import numpy as np
from matplotlib import pyplot as plt
formatterW = plt.matplotlib.ticker.EngFormatter("W")
formatterS = plt.matplotlib.ticker.EngFormatter("s")
formatterJ = plt.matplotlib.ticker.EngFormatter("J")

GLOBAL_R = 680 # Ohm

CLK = 48e6 # Hz
ADC_CLK = 48e6 # Hz

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
# plt.title(f"Total Average Power: {formatterW(av)}")

ax.set_xlim(xmin, xmax)

ticks = ax.get_xticks()
ax.set_xlabel(f"{formatterS(abs(ticks[0] - ticks[1]))}/div")

ax.yaxis.set_major_formatter(formatterW)
ax.xaxis.set_major_formatter(formatterS)
ax.xaxis.set_ticklabels([])
ax.yaxis.set_ticklabels([])
ax.minorticks_on()

ax.grid(which='major', linewidth='1')
ax.grid(which='minor', linewidth='0.25')

ax.plot(time, power, 'k')

tavv = np.zeros(3)
# adc w/ WFI__ & adcto hz to mel
x = xmin + .025
x = [x, x + 1.01]
av = average(time, power, *x)
tavv[0] = (x[1] - x[0])
ax.hlines(av, *x, label=f"{formatterS(x[1] - x[0])}", color='tab:blue')

# packetisation
x = [x[1], x[1] + .0925]
av = average(time, power, *x)
tavv[1] = (x[1] - x[0])
ax.hlines(av, *x, label=f"{formatterS(x[1] - x[0])}", color='tab:green')

# radio w/ WFI__
x = [x[1], x[1] + .135]
av = average(time, power, *x)
tavv[2] = (x[1] - x[0])
ax.hlines(av, *x, label=f"{formatterS(x[1] - x[0])}", color='tab:red')

plt.legend(title='Time Period', framealpha=1)
# plt.show()

tavlab = np.array([
    f"{formatterS(tavv[0])}",
    f"{formatterS(tavv[1])}",
    f"{formatterS(tavv[2])}",
    ])

labels = [
    "Sampling & Spectrogram",
    "Packetisation",
    "Radio Transmission",
    ]

colors = ['tab:blue', 'tab:green', 'tab:red']

fig, ax = plt.subplots(figsize=(7,4) , dpi=120, constrained_layout=True)
ax.pie(tavv, labels=tavlab, colors=colors, autopct='%1.1f%%')
ax.legend(labels, title="Time distribution", framealpha=1, bbox_to_anchor=(1.04, 1))
ax.set_title(f"Total Time: {formatterS(np.sum(tavv))}")
# plt.show()

UpTime = np.array([
    2281219.12/48282728.13,
    4384632.86/4384632.86,
    429443.47 /6608103.24
    ])
print(UpTime*100)

utavlab = np.array([
    f"{formatterS(tavv[0]*UpTime[0])}",
    f"{formatterS(tavv[1]*UpTime[1])}",
    f"{formatterS(tavv[2]*UpTime[2])}",
    ])

fig, ax = plt.subplots(figsize=(7,4) , dpi=120, constrained_layout=True)
ax.pie(tavv*UpTime, labels=utavlab, colors=colors, autopct='%1.1f%%')
ax.legend(labels, title="Up Time distribution", framealpha=1, bbox_to_anchor=(1.04, 1))
ax.set_title(f"Total Up Time: {formatterS(np.sum(tavv*UpTime))}")
plt.show()

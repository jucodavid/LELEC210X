import numpy as np
import matplotlib
from matplotlib import pyplot as plt
formatterW = plt.matplotlib.ticker.EngFormatter("W")
formatterS = plt.matplotlib.ticker.EngFormatter("s")
formatterV = plt.matplotlib.ticker.EngFormatter("V")
formatterJ = plt.matplotlib.ticker.EngFormatter("J")


def move_figure(f, x, y):
    """Move figure's upper left corner to pixel (x, y)"""
    backend = matplotlib.get_backend()
    if backend == 'TkAgg':
        f.canvas.manager.window.wm_geometry("+%d+%d" % (x, y))
    elif backend == 'WXAgg':
        f.canvas.manager.window.SetPosition((x, y))
    else:
        # This works for QT and GTK
        # You can also use window.setGeometry
        f.canvas.manager.window.move(x, y)


GLOBAL_R = 680 # Ohm

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


def plt_setp(ax, xmin, xmax, time, power, X, title, xlabel=False):
    ax.set_title(title, y=1, pad=-14, backgroundcolor='gainsboro')

    ax.set_xlim(xmin, xmax)

    ticks = ax.get_xticks()
    if xlabel: ax.set_xlabel(f"{formatterS(abs(ticks[0] - ticks[1]))}/div")

    ax.yaxis.set_major_formatter(formatterW)
    ax.xaxis.set_major_formatter(formatterS)
    ax.xaxis.set_ticklabels([])
    ax.minorticks_on()

    ax.grid(which='major', linewidth='1')
    ax.grid(which='minor', linewidth='0.25')

    ax.plot(time, power, 'k')

    avv = np.zeros(3)
    tavv = np.zeros(3)

    # adc w/ WFI__ & adcto hz to mel
    x = xmin + X[0]
    x = [x, x + X[1]]
    av = average(time, power, *x)
    avv[0] = av
    tavv[0] = av * (x[1] - x[0])
    ax.hlines(av, *x, label=f"{formatterW(av)}", color='tab:blue')

    # packetisation
    x = [x[1], x[1] + X[2]]
    av = average(time, power, *x)
    avv[1] = av
    tavv[1] = av * (x[1] - x[0])
    ax.hlines(av, *x, label=f"{formatterW(av)}", color='tab:green')

    # radio w/ WFI__
    x = [x[1], x[1] + X[3]]
    av = average(time, power, *x)
    avv[2] = av
    tavv[2] = av * (x[1] - x[0])
    ax.hlines(av, *x, label=f"{formatterW(av)}", color='tab:red')

    # ax.legend(title='Mean Power', framealpha=1, loc='center left')

    return avv, tavv

avvv = np.zeros((6, 3))
tavvv = np.zeros((6, 3))

fig, ax = plt.subplots(6, 1, figsize=(10, 8), dpi=100)

time, power = read("sys_2v2.csv", 2.5)
xmin = -.22
xmax = 1
avvv[0], tavvv[0] = plt_setp(ax[0], xmin, xmax, time, power, [.04, 1.04, .095, .0255], "2.2V")

time, power = read("sys_2v5.csv", 2.5)
xmin = -.35
xmax = .85
avvv[1], tavvv[1] = plt_setp(ax[1], xmin, xmax, time, power, [.04, 1.025, .095, .0255], "2.5V")

time, power = read("sys_2v8.csv", 2.8)
xmin = -.35
xmax = .95
avvv[2], tavvv[2] = plt_setp(ax[2], xmin, xmax, time, power, [.035, 1.015, .095, .13], "2.8V")

time, power = read("sys_3v0.csv", 3.0)
xmin = -.075
xmax = 1.225
avvv[3], tavvv[3] = plt_setp(ax[3], xmin, xmax, time, power, [.0375, 1.01, .095, .135], "3.0V")

time, power = read("sys_3v3.csv", 3.3)
xmin = -.25
xmax = 1.05
avvv[4], tavvv[4] = plt_setp(ax[4], xmin, xmax, time, power, [.05, 1.005, .0925, .13], "3.3V")

time, power = read("sys_3v6.csv", 3.6)
xmin = -.25
xmax = 1.05
avvv[5], tavvv[5] = plt_setp(ax[5], xmin, xmax, time, power, [.04, 1, .095, .13], "3.6V", xlabel=True)

plt.tight_layout()
move_figure(fig, 500, 0)
# plt.show()

fig, ax = plt.subplots(3, 2, figsize=(7,10) , dpi=120, constrained_layout=True)

labels = [
    "Sampling & Spectrogram",
    # "Prints",
    "Packetisation",
    "Radio Transmission",
    # "Hex Encoding & Prints"
    ]

colors = ['tab:blue', 'tab:green', 'tab:red']

titles = ["2.2V", "2.5V", "2.8V", "3.0V", "3.3V", "3.6V"]

for i,tavv in enumerate(tavvv):
    tavlab = np.array([
        f"{formatterJ(tavv[0])}",
        f"{formatterJ(tavv[1])}",
        f"{formatterJ(tavv[2])}",
        # f"{formatterJ(tavv[3])}",
        # f"{formatterJ(tavv[4])}"
        ])

    ax[i//2,i%2].pie(tavv, labels=tavlab, colors=colors, autopct='%1.1f%%')
    ax[i//2,i%2].set_title(titles[i])

move_figure(fig, 500, -200)
# plt.show()

v = np.array([2.2, 2.5, 2.8, 3.0, 3.3, 3.6])

fig, ax = plt.subplots(1, 1, figsize=(10, 5), dpi=100)

ax.plot(v, avvv[:,0], '-o', color='tab:blue', label="Sampling & Spectrogram Calculation")
ax.plot(v, avvv[:,1], '-o', color='tab:green', label="Packetisation")
ax.plot(v[2:], avvv[2:,2], '-o', color='tab:red', label="Radio Transmission")

ax.scatter([2.2, 2.5], avvv[0:2,2], s=200, marker='*', zorder=0, color='tab:red')

ax.yaxis.set_major_formatter(formatterW)
ax.xaxis.set_major_formatter(formatterV)
ax.xaxis.set_ticks(v)
ax.minorticks_on()
ax.grid(which='major', linewidth='1')
ax.grid(which='minor', linewidth='0.25')
ax.legend()
plt.tight_layout()
plt.show()

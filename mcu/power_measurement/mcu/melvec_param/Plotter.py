import numpy as np
import matplotlib
from matplotlib import pyplot as plt
formatterW = plt.matplotlib.ticker.EngFormatter("W")
formatterS = plt.matplotlib.ticker.EngFormatter("s")
formatterHz = plt.matplotlib.ticker.EngFormatter("Hz")
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


def plt_setp(ax, xmin, xmax, time, power, X, title, xlabel=False):
    ax.set_title(title)

    ax.set_xlim(xmin, xmax)

    ticks = ax.get_xticks()
    if xlabel: ax.set_xlabel(f"{formatterS(abs(ticks[0] - ticks[1]))}/div")

    ax.yaxis.set_major_formatter(formatterW)
    ax.xaxis.set_major_formatter(formatterS)
    # ax.xaxis.set_ticklabels([])
    ax.minorticks_on()

    ax.grid(which='major', linewidth='1')
    ax.grid(which='minor', linewidth='0.25')

    ax.plot(time, power, 'k')

    avv = np.zeros(4)
    tavv = np.zeros(4)

    # adc w/ WFI__ & adcto hz to mel
    x = xmin + X[0]
    x = [x, x + X[1]]
    av = average(time, power, *x)
    avv[0] = av
    tavv[0] = av * (x[1] - x[0])
    ax.hlines(av, *x, label=f"{formatterW(av)}", color='tab:blue')

    # prints
    x = [x[1], x[1] + X[2]]
    av = average(time, power, *x)
    avv[1] = av
    tavv[1] = av * (x[1] - x[0])
    ax.hlines(av, *x, label=f"{formatterW(av)}", color='tab:orange')

    # packetisation
    x = [x[1], x[1] + X[3]]
    av = average(time, power, *x)
    avv[2] = av
    tavv[2] = av * (x[1] - x[0])
    ax.hlines(av, *x, label=f"{formatterW(av)}", color='tab:green')

    # hex encode & prints
    x = [x[1], x[1] + X[4]]
    av = average(time, power, *x)
    avv[3] = av
    tavv[3] = av * (x[1] - x[0])
    ax.hlines(av, *x, label=f"{formatterW(av)}", color='tab:purple')

    ax.legend(title='Mean Power', framealpha=1, loc='center left')

    return avv, tavv

avvv = np.zeros((3, 4))
tavvv = np.zeros((3,4))

fig, ax = plt.subplots(3, 1, figsize=(10, 8), dpi=100)

time, power = read("mcu_normal.csv")
xmin = -.55
xmax = 1.1
avvv[0], tavvv[0] = plt_setp(ax[0], xmin, xmax, time, power, [.05, 1.01, .29, .0975, .175], "Normal", xlabel=True)

time, power = read("mcu_doubleLength.csv")
xmin = -.56
xmax = 1.6
avvv[1], tavvv[1] = plt_setp(ax[1], xmin, xmax, time, power, [.05, 1.01, .57, .183, .34], "Double Length", xlabel=True)

time, power = read("mcu_halfSamplePerMelvec.csv")
xmin = -.275
xmax = .86
avvv[2], tavvv[2] = plt_setp(ax[2], xmin, xmax, time, power, [.05, .5, .29, .095, .175], "Half Sample/Melvec", xlabel=True)

plt.tight_layout()
move_figure(fig, 500, 0)
# plt.show()

fig, ax = plt.subplots(3, 1, figsize=(7,10) , dpi=120, constrained_layout=True)

labels = [
    "Sampling & Spectrogram",
    "Prints",
    "Packetisation",
    # "Radio Transmission",
    "Hex Encoding & Prints"]

colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:purple']

titles = ["Normal", "Double Length", "Half Sample/Melvec"]

for i,tavv in enumerate(tavvv):
    tavlab = np.array([
        f"{formatterJ(tavv[0])}",
        f"{formatterJ(tavv[1])}",
        f"{formatterJ(tavv[2])}",
        f"{formatterJ(tavv[3])}",
        # f"{formatterJ(tavv[4])}"
        ])

    ax[i].pie(tavv, labels=tavlab, colors=colors, autopct='%1.1f%%')
    ax[i].set_title(titles[i])

fig.legend(labels, title='Mean Energy', framealpha=1)
move_figure(fig, 500, -200)
plt.show()

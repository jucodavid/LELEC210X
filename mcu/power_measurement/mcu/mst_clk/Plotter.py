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

avvv = np.zeros((10, 3))
tavvv = np.zeros((5, 3))

fig, ax = plt.subplots(5, 1, figsize=(10, 8), dpi=100)

time, power = read("mcu_clk_8MHz.csv")
xmin = -3
xmax = 3.8
avvv[0], tavvv[0] = plt_setp(ax[0], xmin, xmax, time, power, [.1, 5.99, .5475, .1375], "8MHz", xlabel=True)

time, power = read("mcu_clk_16MHz.csv")
xmin = 0.1
xmax = 3.65
avvv[1], tavvv[1] = plt_setp(ax[1], xmin, xmax, time, power, [.1, 3.005, .275, .1375], "16MHz")

time, power = read("mcu_clk_24MHz.csv")
xmin = -.135
xmax = 2.3
avvv[2], tavvv[2] = plt_setp(ax[2], xmin, xmax, time, power, [.1, 2, .185, .135], "24MHz", xlabel=True)

time, power = read("mcu_clk_32MHz.csv")
xmin = -.1
xmax = 1.8
avvv[3], tavvv[3] = plt_setp(ax[3], xmin, xmax, time, power, [.1, 1.5, .14, .136], "32MHz", xlabel=True)

time, power = read("mcu_clk_40MHz.csv")
xmin = 0.025
xmax = 1.55
avvv[4], tavvv[4] = plt_setp(ax[4], xmin, xmax, time, power, [.05, 1.205, .1125, .1345], "40MHz", xlabel=True)

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

titles = ["8MHz", "16MHz", "24MHz", "32MHz", "40MHz"]

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

ax[2,1].axis('off')
fig.legend(labels, title='Mean Energy', framealpha=1, bbox_to_anchor=(.9, .32))
move_figure(fig, 500, 0)
# plt.show()

fig, ax = plt.subplots(5, 1, figsize=(10, 8), dpi=100)

time, power = read("mcu_clk_48MHz.csv")
xmin = 0.175
xmax = 1.45
avvv[5], tavvv[0] = plt_setp(ax[0], xmin, xmax, time, power, [.025, 1.01, .0925, .135], "48MHz")

time, power = read("mcu_clk_56MHz.csv")
xmin = 0.275
xmax = 1.375
avvv[6], tavvv[1] = plt_setp(ax[1], xmin, xmax, time, power, [.015, .8625, .082, .1325], "56MHz")

time, power = read("mcu_clk_64MHz.csv")
xmin = 0.315
xmax = 1.3
avvv[7], tavvv[2] = plt_setp(ax[2], xmin, xmax, time, power, [.015, .7525, .072, .135], "64MHz", xlabel=True)

time, power = read("mcu_clk_72MHz.csv")
xmin = 0.315
xmax = 1.21
avvv[8], tavvv[3] = plt_setp(ax[3], xmin, xmax, time, power, [.015, .6735, .065, .132], "72MHz")

time, power = read("mcu_clk_80MHz.csv")
xmin = 0.41
xmax = 1.23
avvv[9], tavvv[4] = plt_setp(ax[4], xmin, xmax, time, power, [.015, .605, .058, .13], "80MHz", xlabel=True)

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

titles = ["48MHz", "56MHz", "64MHz", "72MHz", "80MHz"]

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

ax[2,1].axis('off')
fig.legend(labels, title='Mean Energy', framealpha=1, bbox_to_anchor=(.9, .32))
move_figure(fig, 500, 0)
# plt.show()

f = np.arange(8e6, 88e6, 8e6)

fig, ax = plt.subplots(1, 1, figsize=(10, 5), dpi=100)

ax.plot(f, avvv[:,0], '-o', color='tab:blue', label="Sampling & Spectrogram Calculation")
ax.plot(f, avvv[:,1], '-o', color='tab:green', label="Packetisation")
ax.plot(f, avvv[:,2], '-o', color='tab:red', label="Radio Transmission")

ax.yaxis.set_major_formatter(formatterW)
ax.xaxis.set_major_formatter(formatterHz)
ax.xaxis.set_ticks(f)
ax.minorticks_on()
ax.grid(which='major', linewidth='1')
ax.grid(which='minor', linewidth='0.25')
ax.legend()
plt.tight_layout()
# plt.show()


def plt_setp(ax, xmin, xmax, time, power, xlabel=False):
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

    # adc to hz to mel
    x = [-.0222, -.018]
    av = average(time, power, *x)
    ax.hlines(av, *x, linestyle='--', label=f"{formatterW(av)}", color='tab:blue')
    ax.legend(title='Mean Power', framealpha=1, loc='center left')

fig, ax = plt.subplots(1, 1, figsize=(10, 5), dpi=100)
time, power = read("mcu_48MHz_zoom.csv")
xmin = -.024
xmax = -.016
plt_setp(ax, xmin, xmax, time, power, xlabel=True)
plt.tight_layout()
plt.show()

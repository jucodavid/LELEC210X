import numpy as np
from matplotlib import pyplot as plt
formatterW = plt.matplotlib.ticker.EngFormatter("W")
formatterS = plt.matplotlib.ticker.EngFormatter("s")


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
    power = data[:,2]**2 / GLOBAL_R
    return time, power

def average(time, power, xmin, xmax):
    i = 0
    while time[i] < xmin:
        i+=1
    j = 0
    while time[j] < xmax:
        j+=1
    return np.mean(power[i:j])


def plt_setp(ax, xmin, xmax, time, power, title, xlabel=False):
    ax.set_title(title)

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

    # adc w/ WFI__ & adcto hz to mel
    x = xmin + .04
    x = [x, x + 1.01]
    av = average(time, power, *x)
    ax.hlines(av, *x, label=f"{formatterW(av)}", color='tab:blue')

    # # packetisation
    # x = [x[1], x[1] + .300 - .0125]
    # av = average(time, power, *x)
    # ax.hlines(av, *x, label=f"{formatterW(av)}", color='tab:orange')

    ax.legend(title='Mean Power', framealpha=1, loc='center left')

fig, ax = plt.subplots(6, 1, figsize=(10, 8), dpi=100)

# time, power = read("mcu_sampling_rate_16MHz.csv")
# xmin = .25
# xmax = 1.3
# plt_setp(ax[0], xmin, xmax, time, power, "18MHz")

# time, power = read("mcu_sampling_rate_48MHz.csv")
# xmin = -.425
# xmax = .625
# plt_setp(ax[1], xmin, xmax, time, power, "48MHz")

# time, power = read("mcu_sampling_rate_80MHz.csv")
# xmin = -.035
# xmax = 1.02
# plt_setp(ax[2], xmin, xmax, time, power, "80MHz", xlabel=True)

plt.tight_layout()
plt.show()


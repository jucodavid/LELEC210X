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



time, power = read("mcu_4.csv")
xmin = -.475
xmax = 1.135

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

# adc w/ WFI__ & adcto hz to mel
x = xmin + .04
x = [x, x + 1.01]
av = average(time, power, *x)
ax.hlines(av, *x, label=f"{formatterW(av)}", color='tab:blue')

# packetisation
x = [x[1], x[1] + .300 - .0125]
av = average(time, power, *x)
ax.hlines(av, *x, label=f"{formatterW(av)}", color='tab:orange')

# setup radio ????
x = [x[1], x[1] + .0975]
av = average(time, power, *x)
ax.hlines(av, *x, label=f"{formatterW(av)}", color='tab:green')

# hex encode
x = [x[1], x[1] + .175]
av = average(time, power, *x)
ax.hlines(av, *x, label=f"{formatterW(av)}", color='tab:purple')

plt.legend(title='Mean Power', framealpha=1)
plt.show()


import numpy as np

import matplotlib.pyplot as plt

x = []
for N in range(4, 17, 2):
    x.append(N)

#y = np.array([0.90953324, 0.02297292, 0.07985298, -0.06252778, 0.02018948, -0.03055926, -0.01129096]) 100paquets
#y = np.array([-0.09958004, -0.01728023, 0.00225266, -0.0142893, -0.00114021, -0.00530857, -0.00126936]) #500paquets
y = np.array([1.20402283e-02, -5.72412149e-03, -9.56333316e-04, -9.34382407e-04, -8.49491811e-04, -5.70236186e-04, -6.90409322e-05])          #2500paquets
#y = np.array([0.03620934, -0.01909011, -0.00079858, 0.00188618, 0.00312197, 0.00537015, 0.00120378]) #1000paquets

#y = np.array([33479.18592352, 15984.4215123, 10622.46179169, 7724.79027858, 5845.98316324, 4504.8187559, 3574.31974748]) #5000paquets, abs
y = np.array([360.79288818, -373.81757305, -19.53176305, 75.19419176, -92.50312615, 49.45926837, -45.60701897])   #2500paquets, no abs

"""
#y2 = np.abs(y)
y3 = np.cumsum(y)
#y4 = y3/y3[-1]

yplot = np.abs(y)/np.abs(y3[-1])*100
yplot2 = np.abs(y3)/np.abs(y3[-1])*100

"""
#y2 = np.abs(y)
tot_corr = np.sum(np.abs(y))
y3 = np.cumsum(np.abs(y))
#y4 = y3/y3[-1]

yplot = np.abs(y)/tot_corr*100
yplot2 = y3/tot_corr*100


fig, ax1 = plt.subplots(figsize=(8, 6))
#Plot yplot à gauche
ax1.plot(x, yplot, marker='o', linestyle='-', color='b')
ax1.set_xlabel('Moose block size (N)')
ax1.set_ylabel('Impact of current N on overall correction (%)', color='b')
ax1.tick_params(axis='y', labelcolor='b')
ax1.grid(True)

#Plot yplot2 à droite
ax2 = ax1.twinx()
ax2.plot(x, yplot2, marker='o', linestyle='-', color='r')
ax2.set_ylabel('Cumulative correction percentage (%)', color='r')
ax2.tick_params(axis='y', labelcolor='r')

plt.title('CFO Correction Evolution')
fig.tight_layout()
plt.show()

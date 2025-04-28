import numpy as np
import matplotlib
from matplotlib import pyplot as plt
formatterW = plt.matplotlib.ticker.EngFormatter("W")
formatterS = plt.matplotlib.ticker.EngFormatter("s")
formatterV = plt.matplotlib.ticker.EngFormatter("V")
formatterJ = plt.matplotlib.ticker.EngFormatter("J")

tavv = np.array([1.35e-3, 115e-6, 135e-6])

tavlab = np.array([
    f"{formatterW(tavv[0])}",
    f"{formatterW(tavv[1])}",
    f"{formatterW(tavv[2])}",
    # f"{formatterJ(tavv[3])}",
    # f"{formatterJ(tavv[4])}"
    ])

labels = [
    "MCU",
    "Radio",
    "AFE",
    ]

fig, ax = plt.subplots(figsize=(7,4) , dpi=120, constrained_layout=True)
ax.pie(tavv, labels=tavlab, autopct='%1.1f%%')
plt.legend(labels, framealpha=1, bbox_to_anchor=(1.04, 1))
plt.title(f"Total power: {formatterW(np.sum(tavv))}")
plt.show()

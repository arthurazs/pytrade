from pathlib import Path

import pandas as pd
from matplotlib import pyplot as plt

filepath = Path("data")
filename = filepath / "1999pub0.csv"

df = pd.read_csv(filename)


fig, ax = plt.subplots(2, 1, constrained_layout=True)

plt.figure(1)
plt.suptitle("Merging Unit", fontsize=18, fontweight="bold")
plt.legend(loc="upper right", fontsize=14)

ax[0].set_ylabel("Sample (A)")
ax[0].set_xlabel("Time")
ax[0].plot(df["us"], df["IAW"], color="red")
ax[0].plot(df["us"], df["IBW"], color="green")
ax[0].plot(df["us"], df["ICW"], color="blue")

ax[1].set_ylabel("Sample (V)")
ax[1].set_xlabel("Time")
ax[1].plot(df["us"], df["VAY"], color="red")
ax[1].plot(df["us"], df["VBY"], color="green")
ax[1].plot(df["us"], df["VCY"], color="blue")

plt.show()

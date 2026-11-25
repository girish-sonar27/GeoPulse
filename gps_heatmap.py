import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

df = pd.read_csv(
    "geolife_gps_data.csv",
    usecols=["Latitude", "Longitude"]
)

# Focus on the Beijing high-density region
df = df[
    (df["Latitude"].between(39.85, 40.10)) &
    (df["Longitude"].between(116.20, 116.50))
]

plt.figure(figsize=(12, 8))

hb = plt.hexbin(
    df["Longitude"],
    df["Latitude"],
    gridsize=80,
    cmap="hot",
    mincnt=1,
    norm=LogNorm()
)

plt.colorbar(hb, label="GPS Point Count (Log Scale)")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("GeoPulse - Beijing GPS Density Heatmap")
plt.grid(alpha=0.2)

plt.savefig("beijing_gps_heatmap.png", dpi=300, bbox_inches="tight")
plt.show()

print("Filtered GPS points:", len(df))
print("Saved: beijing_gps_heatmap.png")

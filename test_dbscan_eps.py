import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN

df = pd.read_csv("beijing_gps_density_clusters.csv")
coords = np.radians(df[["lat_bin", "lon_bin"]].values)

earth_radius_km = 6371.0088

print("EPS TEST RESULTS")
print("-" * 55)

for eps_km in [2, 3, 4, 5, 6, 8, 10]:
    model = DBSCAN(
        eps=eps_km / earth_radius_km,
        min_samples=2,
        metric="haversine",
        algorithm="ball_tree"
    )

    labels = model.fit_predict(coords)
    clusters = len(set(labels) - {-1})
    noise = int((labels == -1).sum())

    print(
        f"EPS: {eps_km:>2} km | "
        f"Clusters: {clusters:>3} | "
        f"Noise: {noise:>3}"
    )

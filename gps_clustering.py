import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN

df = pd.read_csv("beijing_gps_density_clusters.csv")

# Convert coordinates to radians
coords = np.radians(df[["lat_bin", "lon_bin"]].values)

# DBSCAN using Haversine distance
earth_radius_km = 6371.0088
eps_km = 1.5

model = DBSCAN(
    eps=eps_km / earth_radius_km,
    min_samples=2,
    metric="haversine",
    algorithm="ball_tree"
)

df["cluster_id"] = model.fit_predict(coords)

# Cluster summary
summary = (
    df[df["cluster_id"] != -1]
    .groupby("cluster_id")
    .agg(
        total_gps_points=("gps_point_count", "sum"),
        grid_cells=("gps_point_count", "count"),
        center_lat=("lat_bin", "mean"),
        center_lon=("lon_bin", "mean")
    )
    .sort_values("total_gps_points", ascending=False)
)

df.to_csv("gps_clusters.csv", index=False)
summary.to_csv("gps_cluster_summary.csv", index=False)

print("Total density cells:", len(df))
print("Clusters identified:", len(summary))
print("Noise cells:", (df["cluster_id"] == -1).sum())
print("\nTop 10 clusters:")
print(summary.head(10).to_string(index=False))

print("\nSaved gps_clusters.csv")
print("Saved gps_cluster_summary.csv")

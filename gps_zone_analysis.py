import pandas as pd
from sklearn.cluster import KMeans

df = pd.read_csv("beijing_gps_density_clusters.csv")

X = df[["lat_bin", "lon_bin"]].values

kmeans = KMeans(
    n_clusters=3,
    random_state=42,
    n_init=10
)

df["zone_id"] = kmeans.fit_predict(X)

summary = (
    df.groupby("zone_id")
    .agg(
        total_gps_points=("gps_point_count", "sum"),
        grid_cells=("gps_point_count", "count"),
        center_lat=("lat_bin", "mean"),
        center_lon=("lon_bin", "mean")
    )
    .sort_values("total_gps_points", ascending=False)
)

df.to_csv("gps_clusters.csv", index=False)
summary.to_csv("top_retail_zones.csv", index=False)

print("Total GPS cells:", len(df))
print("\nThree exploratory geographic zones:")
print(summary.to_string())

print("\nSaved: gps_clusters.csv")
print("Saved: top_retail_zones.csv")

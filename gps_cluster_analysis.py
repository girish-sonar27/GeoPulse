import pandas as pd

df = pd.read_csv(
    "geolife_gps_data.csv",
    usecols=["Latitude", "Longitude"]
)

df = df[
    df["Latitude"].between(39.85, 40.10) &
    df["Longitude"].between(116.20, 116.50)
].copy()

df["lat_bin"] = df["Latitude"].round(2)
df["lon_bin"] = df["Longitude"].round(2)

clusters = (
    df.groupby(["lat_bin", "lon_bin"])
    .size()
    .reset_index(name="gps_point_count")
    .sort_values("gps_point_count", ascending=False)
)

clusters.to_csv(
    "beijing_gps_density_clusters.csv",
    index=False
)

print("Beijing GPS points:", len(df))
print("Total density cells:", len(clusters))
print("\nTop 20 GPS density cells:")
print(clusters.head(20).to_string(index=False))
print("\nSaved: beijing_gps_density_clusters.csv")

import pandas as pd

f = "geolife_gps_data.csv"
bins = {}
total = 0

for c in pd.read_csv(f, usecols=["Latitude", "Longitude"], chunksize=100000):
    c["lat_bin"] = c["Latitude"].round(2)
    c["lon_bin"] = c["Longitude"].round(2)
    g = c.groupby(["lat_bin", "lon_bin"]).size()

    for k, v in g.items():
        bins[k] = bins.get(k, 0) + int(v)

    total += len(c)

print("Total GPS points:", total)
print("\nTop 15 GPS concentration areas:")
print(pd.Series(bins).sort_values(ascending=False).head(15).to_string())

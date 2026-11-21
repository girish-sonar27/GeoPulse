import math

stores = [
    ("ST001", "GeoPulse Store A", 19.9975, 73.7898),
    ("ST002", "GeoPulse Store B", 19.9990, 73.7950),
    ("ST003", "GeoPulse Store C", 20.0030, 73.7860),
]

radius_m = 500.0
earth_radius_m = 6378137.0

for store_id, name, lat, lon in stores:
    lat_rad = math.radians(lat)
    d_lat = math.degrees(radius_m / earth_radius_m)
    d_lon = math.degrees(radius_m / (earth_radius_m * math.cos(lat_rad)))
    print(f"{store_id} ({name}): lat={lat:.4f} (+-{d_lat:.5f} deg), lon={lon:.4f} (+-{d_lon:.5f} deg) for {radius_m}m")

import pandas as pd

file_path = "geolife_gps_data_v2.csv"

print("Reading GPS dataset...")

chunks = pd.read_csv(file_path, chunksize=500000)

total_rows = 0
missing_rows = 0
invalid_coordinates = 0
duplicate_rows = 0

for chunk in chunks:

    total_rows += len(chunk)

    missing_rows += chunk.isnull().any(axis=1).sum()

    invalid_coordinates += (
        (chunk["Latitude"] < -90) |
        (chunk["Latitude"] > 90) |
        (chunk["Longitude"] < -180) |
        (chunk["Longitude"] > 180)
    ).sum()

    duplicate_rows += chunk.duplicated().sum()

print("\n--- GPS DATA QUALITY REPORT ---")
print("Total Records:", total_rows)
print("Rows with Missing Values:", missing_rows)
print("Invalid Coordinates:", invalid_coordinates)
print("Duplicate Rows:", duplicate_rows)
print("Validation Completed!")
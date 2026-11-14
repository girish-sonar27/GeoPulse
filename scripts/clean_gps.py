import pandas as pd

input_file = "geolife_gps_data_v2.csv"
output_file = "geolife_gps_cleaned.csv"

chunksize = 500000
total_before = 0
total_after = 0

print("Cleaning GPS dataset...")

for i, chunk in enumerate(
    pd.read_csv(input_file, chunksize=chunksize)
):
    total_before += len(chunk)

    # Remove invalid coordinates
    chunk = chunk[
        chunk["Latitude"].between(-90, 90) &
        chunk["Longitude"].between(-180, 180)
    ]

    # Remove exact duplicate rows within each chunk
    chunk = chunk.drop_duplicates()

    total_after += len(chunk)

    chunk.to_csv(
        output_file,
        mode="w" if i == 0 else "a",
        header=(i == 0),
        index=False
    )

print("\nCLEANING COMPLETED!")
print("Original records:", total_before)
print("Cleaned records:", total_after)
print("Removed records:", total_before - total_after)
print("Output:", output_file)

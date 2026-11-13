import csv
from pathlib import Path
from datetime import datetime

# Enter the path to the extracted Data folder
data_path = Path(input("Enter GeoLife Data folder path: ").strip().strip('"'))

# Output CSV
output_file = Path("geolife_gps_data_v2.csv")


columns = [
    "Device_ID",
    "Latitude",
    "Longitude",
    "Altitude_Feet",
    "Excel_Days",
    "Date",
    "Time",
    "Timestamp",
    "Source_File"
]

total_records = 0
total_files = 0

with open(output_file, "w", newline="", encoding="utf-8") as csvfile:

    writer = csv.DictWriter(csvfile, fieldnames=columns)
    writer.writeheader()

    for file in data_path.rglob("*.plt"):

        total_files += 1
        device_id = file.parent.parent.name

        with open(file, "r", encoding="utf-8") as f:

            # Skip the first 6 header lines
            for _ in range(6):
                next(f, None)

            for line in f:
                values = line.strip().split(",")

                if len(values) != 7:
                    continue

                try:
                    latitude = float(values[0])
                    longitude = float(values[1])
                    altitude = float(values[3])

                    date = values[5]
                    time = values[6]

                    timestamp = datetime.strptime(
                        f"{date} {time}",
                        "%Y-%m-%d %H:%M:%S"
                    )

                    writer.writerow({
                        "Device_ID": device_id,
                        "Latitude": latitude,
                        "Longitude": longitude,
                        "Altitude_Feet": altitude,
                        "Excel_Days": values[4],
                        "Date": date,
                        "Time": time,
                        "Timestamp": timestamp,
                        "Source_File": file.name
                    })

                    total_records += 1

                except (ValueError, IndexError):
                    continue

print("\nGPS DATA CONVERSION COMPLETE!")
print("Files processed:", total_files)
print("Total GPS records:", total_records)
print("Output file:", output_file.resolve())
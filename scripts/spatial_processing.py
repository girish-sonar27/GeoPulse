import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
os.environ["SPARK_LOCAL_IP"] = "127.0.0.1"

import os
import pandas as pd

from pyspark.sql import SparkSession
from sedona.spark import SedonaContext

print("Initializing GeoPulse Spatial Processing...")

# Nashik store locations
stores_data = [
    {"store_id": "ST001", "store_name": "GeoPulse Store A", "lat": 19.9975, "lon": 73.7898},
    {"store_id": "ST002", "store_name": "GeoPulse Store B", "lat": 19.9990, "lon": 73.7950},
    {"store_id": "ST003", "store_name": "GeoPulse Store C", "lat": 20.0030, "lon": 73.7860}
]

# Start Spark + Sedona
config = (
    SedonaContext.builder()
    .appName("GeoPulse-Catchment-Processing")
    .master("local[2]")
    .config(
        "spark.jars.packages",
        "org.apache.sedona:sedona-spark-4.0_2.13:1.9.1,"
        "org.datasyslab:geotools-wrapper:1.9.1-33.5"
    )
    .config(
        "spark.jars.repositories",
        "https://artifacts.unidata.ucar.edu/repository/unidata-all"
    )
    .getOrCreate()
)

sedona = SedonaContext.create(config)
sedona.sparkContext.setLogLevel("ERROR")

try:
    stores_df = sedona.createDataFrame(pd.DataFrame(stores_data))
    stores_df.createOrReplaceTempView("stores")

    print("Generating 500-metre catchment polygons...")

    result = sedona.sql("""
        SELECT
            store_id,
            store_name,
            lat,
            lon,

            ST_AsText(
                ST_Transform(
                    ST_Buffer(
                        ST_Transform(
                            ST_SetSRID(ST_Point(lon, lat), 4326),
                            'EPSG:4326',
                            'EPSG:32643'
                        ),
                        500
                    ),
                    'EPSG:32643',
                    'EPSG:4326'
                )
            ) AS catchment_wkt,

            ST_IsValid(
                ST_Buffer(
                    ST_Transform(
                        ST_SetSRID(ST_Point(lon, lat), 4326),
                        'EPSG:4326',
                        'EPSG:32643'
                    ),
                    500
                )
            ) AS is_valid,

            ST_Area(
                ST_Buffer(
                    ST_Transform(
                        ST_SetSRID(ST_Point(lon, lat), 4326),
                        'EPSG:4326',
                        'EPSG:32643'
                    ),
                    500
                )
            ) AS area_sq_m

        FROM stores
    """)

    output_dir = "data/processed"
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "store_catchments.csv")

    result_pd = result.toPandas()
    result_pd.to_csv(output_path, index=False)

    print("\nCatchment generation results:")
    print(result_pd[["store_id", "is_valid", "area_sq_m"]].to_string(index=False))
    print(f"\nSaved output: {output_path}")

    if not result_pd["is_valid"].all():
        raise ValueError("Invalid catchment geometry detected!")

    if not result_pd["area_sq_m"].between(780000, 790000).all():
        raise ValueError("Unexpected catchment area detected!")

    print("\nSUCCESS: All 3 catchment polygons generated and validated.")

finally:
    sedona.stop()

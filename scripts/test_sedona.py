from pyspark.sql import SparkSession
from sedona.spark import SedonaContext

print("Starting Spark + Sedona test...")

config = (
    SedonaContext.builder()
    .appName("GeoPulse-Sedona-Test")
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

result = sedona.sql("""
    SELECT ST_Area(
        ST_GeomFromWKT('POLYGON ((0 0, 10 0, 10 10, 0 10, 0 0))')
    ) AS area
""")

result.show()
print("Sedona spatial function test completed.")

sedona.stop()

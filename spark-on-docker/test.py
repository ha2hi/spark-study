from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark_master_url = "spark://43.201.75.43:7077"

# Create a SparkSession
spark = SparkSession.builder \
   .appName("My App") \
   .master(spark_master_url) \
   .getOrCreate()

rdd = spark.sparkContext.parallelize(range(1, 100))

print("THE SUM IS HERE: ", rdd.sum())
# Stop the SparkSession
spark.stop()
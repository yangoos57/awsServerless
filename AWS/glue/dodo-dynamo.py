import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from datetime import datetime
import pytz

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

# timeset
tz = pytz.timezone("Asia/Tokyo")

today = datetime.now(tz)
year = today.year
month = today.month
day = today.day
time_string = today.strftime("%H%M%S")


dyf = glueContext.create_dynamic_frame.from_catalog(
    database="dodo-glue-db", table_name="dodo_dynamo_db"
)
df = dyf.toDF()

for col in ["user_search", "isbn13_list", "selected_lib"]:
    x = df.select(col).rdd.flatMap(lambda x: x).flatMap(lambda x: x).countByValue()
    new_df = spark.createDataFrame(list(x.items()), ["keyword", "counts"])
    new_df = new_df.orderBy("count", ascending=False)
    new_df.coalesce(1).write.format("parquet").save(
        f"s3://dodomoabucket/dodo-glue/dodo-dynamo/{col}/{year}/{month}/{day}/{time_string}"
    )

job.commit()

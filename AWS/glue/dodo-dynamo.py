import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from datetime import datetime
from pyspark.sql.functions import explode
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
df.coalesce(1).write.format("parquet").save(
    f"s3://dodomoabucket/dodo-glue/dodo-dynamo/db_dynamo/{year}/{month}/{day}/{time_string}"
)


df_isbn13 = df.select(df.query_id, explode(df["isbn13_list"])).toDF("query_id", "isbn13")
df_isbn13.coalesce(1).write.format("parquet").save(
    f"s3://dodomoabucket/dodo-glue/dodo-dynamo/isbn_13/{year}/{month}/{day}/{time_string}"
)


df_selected_lib = df.select(df.query_id, explode(df["selected_lib"])).toDF("query_id", "lib")
df_selected_lib.coalesce(1).write.format("parquet").save(
    f"s3://dodomoabucket/dodo-glue/dodo-dynamo/selected_lib/{year}/{month}/{day}/{time_string}"
)


df_user_search = df.select(df.query_id, explode(df["user_search"])).toDF("query_id", "keyword")
df_user_search.coalesce(1).write.format("parquet").save(
    f"s3://dodomoabucket/dodo-glue/dodo-dynamo/user_search/{year}/{month}/{day}/{time_string}"
)


job.commit()

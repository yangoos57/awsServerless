import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.sql.functions import count
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from datetime import datetime
import pytz

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ["JOB_NAME"])

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

# job init
job.init(args["JOB_NAME"], args)
spark = glueContext.spark_session
connection_mysql8_options = {
    "url": "jdbc:mysql://dodomoards.ccoalf3s8d7c.ap-northeast-2.rds.amazonaws.com:3306/dodomoa_db",
    "dbtable": "user_choice",
    "user": "admin",
    "password": "1q2w3e4r!",
    "customJdbcDriverS3Path": "s3://dodomoabucket/mysql-jar/mysql-connector-j-8.0.32/mysql-connector-j-8.0.32.jar",
    "customJdbcDriverClassName": "com.mysql.cj.jdbc.Driver",
}

df_mysql8 = glueContext.create_dynamic_frame.from_options(
    connection_type="mysql", connection_options=connection_mysql8_options
)
rds_df = df_mysql8.toDF()

for col in ["isbn13", "user_id"]:
    new_df = rds_df.groupBy(col).agg(count("*").alias("count"))
    new_df = new_df.orderBy("count", ascending=False)
    new_df.show()
    new_df.coalesce(1).write.format("parquet").save(
        f"s3://dodomoabucket/dodo-glue/dodo-rds/{col}/{year}/{month}/{day}/{time_string}"
    )

job.commit()

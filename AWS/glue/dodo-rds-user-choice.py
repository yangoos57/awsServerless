import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.sql.functions import count
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from datetime import datetime
import logging
import pytz

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ["JOB_NAME"])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

logger = glueContext.get_logger()
logger.info("connection success!!")

# timeset
tz = pytz.timezone("Asia/Tokyo")

today = datetime.now(tz)
year = today.year
month = today.month
day = today.day
time_string = today.strftime("%H%M%S")

# job init
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
ps_df = df_mysql8.toDF()
logger.info("loading df_mysql8 success!")

jbdc_url = "jdbc:redshift://dodo-redshift.cqxeoifnc1we.ap-northeast-2.redshift.amazonaws.com:5439/dev?user=admin&password=Admin111!"
# Write the DataFrame to Redshift
ps_df.write.format("com.databricks.spark.redshift").option("url", f"{jbdc_url}",).option(
    "dbtable", "user_chocie"
).option("tempdir", "s3://aws-glue-assets-965780743476-ap-northeast-2/temp/").option(
    "aws_iam_role", "arn:aws:iam::965780743476:role/service-role/AWSGlueServiceRole"
).mode(
    "append"
).save(
    f"s3://dodomoabucket/dodo-glue/dodo-rds/rds/{year}/{month}/{day}/{time_string}"
)

# rds_df = df_mysql8.toDF().save(
#     f"s3://dodomoabucket/dodo-glue/dodo-rds/dodo-rds/{year}/{month}/{day}/{time_string}"
# )
job.commit()

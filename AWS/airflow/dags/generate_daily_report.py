from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.providers.amazon.aws.operators.redshift_data import RedshiftDataOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import python_operator.functions as op_fc
import pytz
from datetime import datetime
from airflow import DAG
import os
import boto3
import pandas as pd

DAG_ID = os.path.basename(__file__)
glue_job_name = "dodo-rds-user-choice-etl"
bucket_name = "aws-glue-assets-965780743476-ap-northeast-2"
role_name = "AWSGlueServiceRole"

tz = pytz.timezone("Asia/Tokyo")
today = datetime.now(tz)
year = today.year
month = today.month
day = today.day

dynamo_db_raw_dir = f"data/dynamo-db-raw/{year}/{month}/{day}"


with DAG(
    dag_id=DAG_ID,
    schedule="@once",
    start_date=datetime(2023, 5, 19),
    tags=["example"],
    catchup=False,
) as dag:

    task1_1 = GlueJobOperator(
        task_id="extract_rds_to_s3",
        job_name=glue_job_name,
        script_location=f"s3://{bucket_name}/scripts/dodo-rds-user-choice-etl.py",
        s3_bucket=bucket_name,
        iam_role_name=role_name,
        create_job_kwargs={"GlueVersion": "3.0", "NumberOfWorkers": 2, "WorkerType": "G.1X"},
    )

    # task1_2 = PythonOperator(
    #     task_id="extract_dynamo_db_to_local",
    #     python_callable=op_fc.extract_dynamo_db_to_local,
    #     op_args=[dynamo_db_raw_dir, True],
    # )
    # task2 = PythonOperator(
    #     task_id="transform_dynamo_db",
    #     python_callable=op_fc.transform_dynamo_db,
    #     op_args=[dynamo_db_raw_dir],
    # )

    # task3 = BashOperator(
    #     task_id="extract_transformed_data_to_s3",
    #     bash_command="aws s3 sync data/result/ s3://dodomoabucket/dodo-glue/dodo-dynamo/",
    # )
    task1_1
    # [task1_1, task1_2] >> task2 >> task3

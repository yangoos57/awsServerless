from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from datetime import datetime
from airflow import DAG
import os

DAG_ID = os.path.basename(__file__)

glue_job_name = "dodo-rds-user-choice-etl"
bucket_name = "dodomoabucket"
role_name = "AWSGlueServiceRole"

with DAG(
    dag_id=DAG_ID,
    schedule="@once",
    start_date=datetime(2021, 1, 1),
    tags=["example"],
    catchup=False,
) as dag:
    submit_glue_job = GlueJobOperator(
        task_id="submit_glue_job",
        job_name=glue_job_name,
        script_location=f"s3://aws-glue-assets-965780743476-ap-northeast-2/scripts/dodo-rds-user-choice-etl.py",
        s3_bucket=bucket_name,
        iam_role_name=role_name,
        create_job_kwargs={"GlueVersion": "3.0", "NumberOfWorkers": 2, "WorkerType": "G.1X"},
    )

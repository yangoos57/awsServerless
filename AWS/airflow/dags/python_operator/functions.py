from pyspark.sql import SparkSession
from datetime import datetime
from pyspark.sql.functions import explode, size
import pytz
import boto3
import pandas as pd
import os


def transform_dynamo_db(dir: str):
    """
    preprocess data from dynamo DB and RDS
    """
    # timeset
    tz = pytz.timezone("Asia/Tokyo")
    today = datetime.now(tz)
    year = today.year
    month = today.month
    day = today.day
    # start pyspark session
    spark = SparkSession.builder.getOrCreate()

    # load raw dynamo db file
    df = spark.read.parquet(f"{dir}/dynamo-db.parquet")

    # explode isbn13
    df_isbn13 = df.select(df.query_id, explode(df["isbn13_list"])).toDF("query_id", "isbn13")
    df_isbn13.coalesce(1).write.format("parquet").mode("overwrite").save(
        f"data/result/{year}/{month}/{day}/isbn_13"
    )

    # explode lib
    df_selected_lib = df.select(df.query_id, explode(df["selected_lib"])).toDF("query_id", "lib")
    df_selected_lib.coalesce(1).write.format("parquet").mode("overwrite").save(
        f"data/result/{year}/{month}/{day}/selected_lib"
    )

    # explode success_user_search
    df_success_user_search = df.filter(size(df["isbn13_list"]) > 0)
    df_success_user_search = df_success_user_search.select(
        df_success_user_search.query_id, explode(df["user_search"])
    ).toDF("query_id", "keyword")
    df_success_user_search.coalesce(1).write.format("parquet").mode("overwrite").save(
        f"data/result/{year}/{month}/{day}/success_user_search"
    )

    # explode failed_user_search
    df_failed_user_search = df.filter(size(df["isbn13_list"]) == 0)
    df_failed_user_search = df_failed_user_search.select(
        df_failed_user_search.query_id, explode(df_failed_user_search["user_search"])
    ).toDF("query_id", "failed_keyword")
    df_failed_user_search.coalesce(1).write.format("parquet").mode("overwrite").save(
        f"data/result/{year}/{month}/{day}/failed_user_search"
    )


def extract_dynamo_db_to_local(dir: str, test):
    """
    extract dynamo db table to local and save it as parquet
    """
    # timeset

    _check_directory(dir)

    # Create a DynamoDB client
    dynamodb = boto3.resource("dynamodb")

    # Specify the table name
    table_name = "dodo-dynamo-db"

    # Get a reference to the DynamoDB table
    table = dynamodb.Table(table_name)
    print(table)

    # Scan the entire table and retrieve all items
    response = table.scan()

    if test == True:
        """정상작동여부 테스트"""
        print("you select test_mode. Only 1500 items will be saved.")
        task = response["Items"]
    else:
        print("you don't select test_mode. whole items will be saved.")
        task = response["Items"]
        while "LastEvaluatedKey" in response:
            response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            task += response["Items"]
        task = response["Items"]

    x = pd.DataFrame(task)
    x.to_parquet(f"{dir}/dynamo-db.parquet", compression="snappy")
    print(f"successfully saved_dynamo_db_items_to_dirctory : {dir}")


def _check_directory(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Directory '{directory_path}' created successfully.")

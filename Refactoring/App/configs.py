import os

# url = os.getenv("DB_URL")
# user = os.getenv("MYSQL_USER")
# password = os.getenv("MYSQL_PASSWORD")

url = "127.0.0.1"
user = "root"
password = 1234

print(user, password)


class Deployment:
    db_dir = f"mysql+pymysql://{user}@{url}:3306"
    # db_dir = f"mysql+pymysql://{user}:{password}@{url}:3306"
    db_name = "dodomoa_db"
    api_auth_key = "7123eacb2744a02faca2508a82304c3bf154bf0b285da35c2faa2b8498b09872"


class Test:
    db_dir = f"mysql+pymysql://{user}:{password}@{url}:3306"
    db_name = "dodomoa_test"

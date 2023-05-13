from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from configs import Deployment
from uuid import uuid4
from search import BookSearcher
import json

# Env
env = Deployment()

# Load Book Search Class
book_searcher = BookSearcher()

# DB Session using Sqlalchemy.orm
SQLALCHEMY_DATABASE_URL = f"{env.db_dir}/{env.db_name}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
print("Session Connected!")


def handler(event, context):
    print(event)
    try:
        book_df = book_searcher.create_book_recommandation_df(session, event).to_dict("records")
        resp = True
    except KeyError as e:
        book_df = {}
        resp = False

    return {
        "user_search": event["user_search"],
        "selected_lib": event["selected_lib"],
        "response": resp,
        "table_id": str(uuid4()),
        "result": book_df,
    }


# if __name__ == "__main__":
#     test_data = {"user_search": ["도커"], "selected_lib": ["양천"]}
#     print(lambda_handler(request_data=test_data, context="t"))

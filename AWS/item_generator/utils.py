from random import randint
import requests

# env
api_url = "https://api.yangoos.me"


def generate_book_item_indices(v):
    random_counts = randint(1, int(v * 0.25) + 1)
    return [randint(0, v) for _ in range(random_counts)]


def generate_user_id():
    return f"user-{randint(1000,1999)}"


def requests_book_items(book_payload):
    req_for_book_items = requests.post(api_url + "/predict", json=book_payload)
    return req_for_book_items.json()


# lambda function
def record_user_choice(user_id, query_id, isbn13):
    payload = {"user_id": user_id, "query_id": query_id, "isbn13": isbn13}
    return requests.post(api_url + "/user-choice", json=payload)

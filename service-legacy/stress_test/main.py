from locust import HttpUser, task, between
from random import randint


class User(HttpUser):
    @task
    def predict_iris(self):
        wait_time = between(1, 2)

        first = randint(0, 9)
        second = randint(0, 9)

        key = ["파이토치", "파이썬", "pandas", "데이터", "분석", "자바스크립트", "도커", "mysql", "java", "AI"]
        lib = ["강남", "강동", "강서", "개포", "고덕", "고척", "구로", "남산", "노원", "도봉"]

        payloads = dict(
            user_search=[key[first], key[second]], selected_lib=[lib[first], lib[second]]
        )

        self.client.post(
            "/predict",
            json=payloads,
        )

    def on_start(self):
        print("START LOCUST")

    def on_stop(self):
        print("STOP LOCUST")

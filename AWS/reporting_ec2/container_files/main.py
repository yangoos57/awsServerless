from fastapi import FastAPI
from utils import create_report

# Create an instance of the FastAPI application
app = FastAPI()

# Define a route and its corresponding function
@app.get("/report/{date_time}")
def read_root(date_time: str = "2023-05-17"):
    print(date_time)
    create_report(date_time)

    return {"status": "200", "body": "ok"}

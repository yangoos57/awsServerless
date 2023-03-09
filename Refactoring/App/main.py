from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers.routers import router

app = FastAPI()

app.include_router(router, prefix="", tags=[""])

app.mount("/", StaticFiles(directory="static"), name="static")

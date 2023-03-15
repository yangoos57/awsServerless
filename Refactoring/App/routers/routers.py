from fastapi import APIRouter, Depends, BackgroundTasks, Request
from db.database import get_db, Base, engine
from db.schemas import BookInfoSchemas
from routers.schemas import *
import db.cruds as query
from sqlalchemy.orm import Session
from configs import Deployment
from typing import *
from uuid import uuid4
import pandas as pd
import numpy as np
from .search import BookSearcher

router = APIRouter()
Base.metadata.create_all(bind=engine)
query.upload_data_when_init(db=next(get_db()))
book_searcher = BookSearcher()


@router.get("/health")
def health() -> Dict[str, str]:
    return {"health": "ok"}


@router.post("/predict")
def predict(data: Data, background_task: BackgroundTasks, db: Session = Depends(get_db)):
    print(data.dict())
    # predict data
    uuid = str(uuid4())
    request_data = data.dict()
    print(request_data["user_search"][0])
    book_df = book_searcher.create_book_recommandation_df(db, request_data)

    # process register_items_to_db after responses
    # background_task.add_task(register_items_to_db, df, uuid)

    return {
        "user_search": request_data["user_search"],
        "selected_lib": request_data["selected_lib"],
        "table_id": uuid,
        "result": book_df.to_dict("records"),
    }


@router.post("/update/book-info")
def test(data: BookInfoSchemas, background_task: BackgroundTasks, db: Session = Depends(get_db)):
    return query.update_db(db, "book_info", data)


@router.post("/update/lib-books")
def test(data: LibBookSchemas, background_task: BackgroundTasks, db: Session = Depends(get_db)):
    return query.update_db(db, "lib_books", data)

from fastapi import APIRouter, Depends, BackgroundTasks, Request
from fastapi.templating import Jinja2Templates
from metrics.metrics import update_dashboard
from db.database import get_db, Base, engine
from db.schemas import BookInfoSchemas
from routers.schemas import *
import db.cruds as query
from sqlalchemy.orm import Session
from configs import Deployment
from typing import Dict, Union, List
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
    # predict data
    uuid = str(uuid4())
    user_search = data.dict()["user_search"]
    book_isbn = book_searcher.extract_recommand_book_isbn(user_search)

    selected_lib = data.dict()["selected_lib"]
    lib_name_info = query.load_lib_name_info(db, book_isbn, selected_lib)

    lib_book_data = pd.DataFrame(lib_name_info)
    lib_book_data = pd.DataFrame(lib_name_info).groupby(by="isbn13").agg(list).reset_index()

    book_info = query.load_book_info(db, lib_book_data.isbn13.tolist())
    book_info_db = pd.DataFrame(book_info)

    result_df = book_info_db.merge(lib_book_data, on="isbn13")
    old_idx = result_df.isbn13.get_indexer(book_isbn)
    print(old_idx)
    order_rank = np.delete(old_idx, np.where(old_idx == -1), axis=0)

    result_df = result_df.iloc[order_rank].reset_index(drop=True)
    print(result_df)

    # # def register_items_to_db(df: pd.DataFrame, uuid: List[str]):
    # #     # create rows in the prediction_table
    # #     df["id"] = uuid
    # #     df["Transported_prediction"] = prediction
    # #     df_dict = df.to_dict(orient="records")
    # #     register_items(db, df_dict)

    # # process register_items_to_db after responses
    # # background_task.add_task(register_items_to_db, df, uuid)

    # return {
    #     "user_search": user_search,
    #     "selected_lib": selected_lib,
    #     "data": {"table_id": uuid, "result": book_info_sort.to_dict("records")},
    # }


@router.post("/update/book-info")
def test(data: BookInfoSchemas, background_task: BackgroundTasks, db: Session = Depends(get_db)):
    query.update_db(db, "book_info", data)
    return {"h": "h"}


@router.post("/update/lib-books")
def test(data: LibBookSchemas, background_task: BackgroundTasks, db: Session = Depends(get_db)):
    query.update_db(db, "lib_books", data)
    return {"h": "h"}

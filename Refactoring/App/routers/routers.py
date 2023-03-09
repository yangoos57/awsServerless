from fastapi import APIRouter, Depends, BackgroundTasks, Request
from fastapi.templating import Jinja2Templates
from metrics.metrics import update_dashboard
from db.database import get_db, Base, engine
from routers.schemas import Data, Result
from db.cruds import *
from sqlalchemy.orm import Session
from configs import Deployment
from typing import Dict, Union
from uuid import uuid4
import pandas as pd
import numpy as np
import joblib

router = APIRouter()
Base.metadata.create_all(bind=engine)
pipe = joblib.load("../models/random_forest.pkl")


@router.get("/health")
def health() -> Dict[str, str]:
    return {"health": "ok"}


@router.post("/predict")
def predict(data: Data, background_task: BackgroundTasks, db: Session = Depends(get_db)):
    # predict data
    df = pd.DataFrame(data.dict(), columns=Deployment.columns)
    prediction: np.ndarray = pipe.predict(df)

    uuid = [str(uuid4()) for _ in range(len(df))]

    def register_items_to_db(df: pd.DataFrame, uuid: List[str]):
        # create rows in the prediction_table
        df["id"] = uuid
        df["Transported_prediction"] = prediction
        df_dict = df.to_dict(orient="records")
        register_items(db, df_dict)

    # process register_items_to_db after responses
    background_task.add_task(register_items_to_db, df, uuid)

    return {
        "model_name": "Random-Forest",
        "type": "Classifier",
        "version": "v0.1",
        "data": {"table_id": uuid, "prediction": prediction.tolist()},
    }


@router.post("/result", status_code=201)
def result(data: List[Result], db: Session = Depends(get_db)):
    # update Adaptivity_Level in the prediction_table
    data = [d.dict() for d in data]
    register_Transported(db, data)

    return data


@router.get("/dash")
def dash(request: Request, db: Session = Depends(get_db)):
    templates = Jinja2Templates(directory="static/metrics")

    # update Dashboard
    prev = 0
    num_rows: int = get_num_rows(db)
    if num_rows - prev > 0:
        True_Prediction: List(Tuple[bool, bool]) = get_true_and_prediction_col(db)
        print(True_Prediction)
        df = pd.DataFrame(True_Prediction)
        update_dashboard(df)
        prev = num_rows

    return templates.TemplateResponse("model_metrics.html", {"request": request})


@router.get("/test")
def dash(request: Request, db: Session = Depends(get_db)):
    print(test(db))

import db.schemas as schema
import db.table as table
from sqlalchemy.orm import Session
from typing import List, Dict, Tuple
from logs.utils import make_logger

logger = make_logger("logs/main.log", __name__)


def select_all_items(db: Session, limit: int = 100) -> List[schema.PredictionCreate]:
    return db.query(table.Prediction).limit(limit).all()


def register_item(db: Session, feature: schema.PredictionCreate):
    feature = table.Prediction(**feature)
    db.add(feature)
    db.commit()
    return feature


def register_items(db: Session, features: List[schema.PredictionCreate]):
    for feature in features:
        register_item(db=db, feature=feature)
    return features


def select_by_id(db: Session, id: str) -> schema.PredictionCreate:
    return db.query(table.Prediction).filter(table.Prediction.id == id).first()


def register_Transported(db: Session, results: List[Dict[str, str]]):
    for result in results:
        values = [x for x in result.values()]
        item = select_by_id(db=db, id=values[0])
        item.Transported = values[1]
        db.commit()
        # db.refresh(item)
    return results


def delete_items(db: Session, ids: List[str]):
    for id in ids:
        db.query(table.Prediction).filter(table.Prediction.id == id).delete()

    return ids


def get_num_rows(db: Session) -> int:
    return db.query(table.Prediction).count()


def get_true_and_prediction_col(db: Session, limit: int = 200) -> List[Tuple[bool, bool]]:
    return (
        db.query(table.Prediction.Transported, table.Prediction.Transported_prediction)
        .filter(table.Prediction.Transported != None)
        .order_by(table.Prediction.Date.desc())
        .limit(limit)
        .all()
    )


def test(db: Session, limit: int = 200) -> List[Tuple[str, str]]:
    return db.query(table.Prediction.Date).limit(limit).all()

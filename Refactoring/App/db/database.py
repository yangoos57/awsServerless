from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from configs import Deployment

SQLALCHEMY_DATABASE_URL = f"{Deployment.db_dir}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

if not database_exists(f"{Deployment.db_dir}/{Deployment.db_name}"):
    create_database(f"{Deployment.db_dir}/{Deployment.db_name}")


SQLALCHEMY_DATABASE_URL = f"{Deployment.db_dir}/{Deployment.db_name}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

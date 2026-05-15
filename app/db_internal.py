from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTERNAL_DATABASE_URL = f"sqlite:///{BASE_DIR}/internal.db"

internal_engine = create_engine(INTERNAL_DATABASE_URL, connect_args={"check_same_thread": False})
InternalSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=internal_engine)
InternalBase = declarative_base()


def get_internal_db():
    db = InternalSessionLocal()
    try:
        yield db
    finally:
        db.close()

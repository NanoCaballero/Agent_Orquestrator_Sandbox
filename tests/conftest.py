import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base, get_db
from app.main import app
from seed.seed_db import seed as run_seed

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use a fresh in-memory DB for each test session
TEST_DB_URL = "sqlite:///./test_bank.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Patch the engine used by models so seed creates tables in test_bank.db
    import app.db as db_module
    original_engine = db_module.engine
    original_session = db_module.SessionLocal

    db_module.engine = test_engine
    db_module.SessionLocal = TestSessionLocal
    Base.metadata.create_all(bind=test_engine)

    run_seed()

    yield

    db_module.engine = original_engine
    db_module.SessionLocal = original_session
    if os.path.exists("test_bank.db"):
        os.remove("test_bank.db")


@pytest.fixture
def client(setup_test_db):
    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
